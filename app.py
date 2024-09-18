import eventlet

# Monkey patching to make standard library cooperative
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
from Helper import TextHandler
from flask import Flask, flash, request, redirect
import random
import os
from dotenv import load_dotenv
from functools import lru_cache
from Helper import utils
from Helper import Speech2Text
from Helper import LlamaRec
from Helper import TextToEmbeddings
import uuid
from sentence_transformers import SentenceTransformer
import numpy as np
from faster_whisper import WhisperModel
from langchain_groq import ChatGroq
import json
from pymongo import MongoClient
from bson import json_util
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins":  ["*"]}})
CORS(app, resources={r"/save-record": {"origins": "*"}})
CORS(app, resources={r"/text-to-embedding": {"origins": "*"}})
CORS(app, resources={r"/save-record-unity": {"origins": "*"}})

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

model = SentenceTransformer('all-MiniLM-L6-v2')

model_size = "base"
text_model = WhisperModel(model_size,  device="cpu")

llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_CLOUD"), 
            model_name="llama-3.1-70b-versatile"
    )

mongodb = os.getenv("MONGODB_URI")

client = MongoClient(mongodb)

db = client['testDB']
ad_collection = db['ads']

# ================================================================ UTILITY FUNCTION ================================================

def saveRecordedFile(request):
# check if the post request has the file part
    # print(request.files)
    if 'file' not in request.files:
        print("err")
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    file_name = str(uuid.uuid4()) + ".wav"
    full_file_name = os.path.join("Data", file_name)


    try:
        full_file_name = os.path.join("Data", file_name)
        file.save(full_file_name)
        return full_file_name

    except:
        print("error")

    return "error"

def normalize_embedding(embedding):
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

def getEmbedding(text):
    if isinstance(text, str):
        embeddings = model.encode([text])
        return embeddings.tolist()

def query_db(vector):
    try:
        results = ad_collection.aggregate([
            {
                "$search": {
                    "index": "AdSearch",  # Replace with your actual index name
                    "knnBeta": {
                        "vector": vector,
                        "path": "embedding",
                        "k": 3
                    }
                }
            },
            {
                "$match": {"available_balance": {"$gt": 0.01}}  # Filter documents with available_balance > 0.01
            },
            {
                "$project": {
                    "score": {"$meta": "searchScore"},
                    "document": "$$ROOT"
                }
            }
        ])
            
        return list(results)
    except Exception as e:
        print(f"Err during vector search: {str(e)}")
    
    return []
    


def stage1(customer_verdict):

    promp_ph1 =f"""CUSTOMER Feedback:\n{customer_verdict}\nINSTRUCTION:\nReturn a JSON object with a single key products containing an array of recommended products based on customer data. Omit any additional text or keys. The output should be a valid JSON string in the exact format below:\n{{"products":["product 1", "product 2", ... , "product n"]}}\nRESPONSE(NO PREAMBLE):"""

    response = llm.invoke(promp_ph1)
    try:
        json_data = json.loads(response.content)
        return json_data
    except:
        print("invalid json",response.content)
        return {"products": []}
    
def stage2(product_list):
    retrieved_items = []
    for i in product_list:
        # Convert it to embeddings
        product_embedding = getEmbedding(i)

        # perform db query
        result = query_db(product_embedding[0])
        
        # return id, image and name
        retrieved_items.append(result)

    # BSON to json VERY IMP
    return json.loads(json_util.dumps(retrieved_items))

def stage3(str, customer_verdict):
    prompt = f"""INSTRUCTION:
    Filter the predicted demand list: {str} to return the most relevant product that matches the customer's demand {customer_verdict}. If no relevant product exists, return an empty list. Exclude any unrelated products. The output should be a valid JSON string in the exact format below, without any additional text or keys:
    {{"products":["product 1", "product 2", ... , "product n"]}}
    RESPONSE(NO PREAMBLE):
    """

#     print("\n\n\n",prompt,"\n\n\n")

    response = llm.invoke(prompt)
    try:
#         print(response.content)
        json_data =json.loads(response.content)
        return json_data
    except:
        print("invalid json ", response.content)
        return {"products": []}
    
    
def LLamaRec(customer_verdict):
    print("Customer -> ", customer_verdict)
    # STAGE 1
    stage1_data = stage1(customer_verdict)
    print("Stage 1 -> ", stage1_data)
#     TODO: Implement err handling
#     if(len(stage1_data) == 0):
#         return

    # STAGE 2
    stage2_data = stage2(stage1_data["products"])

#     Unique products  
    unique_elements = set()
    filtered_list = []
    for i in stage2_data:
        for j in i:
            filtered_data = (
                ("id", j["document"]["_id"]["$oid"]),
                ("name", j["document"]["name"]),
                ("image", j["document"]["image"]),
            )
            if filtered_data not in unique_elements:
                unique_elements.add(filtered_data)
                filtered_list.append(dict(filtered_data))
            
#     Unique products names
    filtered_prod_name = ""
    for i in filtered_list:
        filtered_prod_name = filtered_prod_name + "`" + i['name'] + "`,"
    
    filtered_prod_name = filtered_prod_name[:len(filtered_prod_name)-2]
    
    print("Stage 2(Vector search) filtered - > ", filtered_prod_name)
#     # STAGE 3
    final_products_name = stage3(filtered_prod_name, customer_verdict)
    final_products_list = []
    
    for i in filtered_list:
        if  i['name'] in final_products_name['products']:
            final_products_list.append(i)
    
    
    print("Stage(Ranking) 3 -> ", final_products_list)
    return final_products_list


def speech2text(file_path):
    segments, info = text_model.transcribe(file_path, beam_size=5)
    
    txt = ""

    for segment in segments:
        txt = txt + segment.text

    return txt

# ============================================================== HTTP ROUTES =======================================================================

# Html Routes
@app.route("/", methods=['GET'])
def hello_world():
    return "Hello"
    

@app.route("/text-to-embedding", methods=['POST'])
@cross_origin()
def sendEmbedding():
    data = request.get_json()
    text = data["text"]
    embedding = getEmbedding(text)
    
    if(embedding):
        return embedding
    else:
        print("Please provide a string.")

    return "error"

@app.route('/save-record', methods=['POST'])
@cross_origin()
def save_record():

    file_path = saveRecordedFile(request)
    print(file_path)
    if(file_path == 'error'):
        return "error"
    
    # Speech 2 text
    customer_data = speech2text(file_path)
    if(len(customer_data)<1):
        print(customer_data)
        return []
    print("Speech 2 text -> ",customer_data)

    # LLamaRec
    response = LLamaRec(customer_data)
    
    return response
  
    # TODO: Save ads to user db(MONGO DB)
    
@app.route('/save-record-unity', methods=['POST'])
@cross_origin()
def save_record_unity():

    file_path = saveRecordedFile(request)
    print(file_path)
    if(file_path == 'error'):
        print("error")
        return []
    
    # # Speech 2 text
    customer_data = speech2text(file_path)
    if(len(customer_data)<1):
        print(customer_data)
        return []
    print(customer_data)

    # customer_data="Laptop"
    # LLamaRec
    response = LLamaRec(customer_data)
    
    return response

# ================================================================= Socket events ==================================================================

@socketio.on("textIn")
def handle_msg(args):
    """
        Takes text as inputs, pre-process text , then convert text to vector embedding, do similar search, rank it using llm and return ads

        Args:
            args -> text
    """
    
    handler = TextHandler()
    # Creating new threads for each user text req
    eventlet.spawn_n(handler.sendResponse, args, request.sid, socketio, eventlet)
    

@socketio.on("connect")
def handle_connect():
    # print(f"Client connected with socket ID>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  {request.sid}")
    pass
    

@socketio.on("disconnect")
def handle_disconnect():
    # print(f"Client disconnected with socket ID >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {request.sid}")
    pass


if __name__ == '__main__':
    socketio.run(app, debug=False, port=5000, host="0.0.0.0")