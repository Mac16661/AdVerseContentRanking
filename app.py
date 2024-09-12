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


socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

model = SentenceTransformer('all-MiniLM-L6-v2')

model_size = "tiny.en"
text_model = WhisperModel(model_size,  compute_type="int8")

llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_CLOUD"), 
            model_name="llama-3.1-70b-versatile"
    )

client = MongoClient("mongodb+srv://admin:UB3C2ro6pUVUPPqg@cluster0-test.eyqrt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0-test")

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
                        "k": 2
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
    except:
        print("Err during vector search")
    
    return []
    


def stage1(customer_verdict):
    # customer_verdict = "I like softdrinks"

    promp_ph1 =f"""CUSTOMER Feedback:\n{customer_verdict}\nINSTRUCTION:\nReturn a JSON object with a single key products containing an array of recommended products based on customer data. Omit any additional text or keys. The output should be a valid JSON string in the exact format below:\n{{"products":["product 1", "product 2", ... , "product n"]}}\nRESPONSE(NO PREAMBLE):"""

    response = llm.invoke(promp_ph1)
    try:
        json_data =json.loads(response.content)
        return json_data
    except:
        print("invalid json")
        return {"products": []}
    
def stage2(product_list):
    # retrieved_items = []
    # for i in product_list:
        # print(i)
        # Convert it to embeddings
        # product_embedding = getEmbedding(i)

        # perform db query
        # result = query_db(product_embedding)
        
        # return id, image and name
        # retrieved_items.append(result)

    retrieved_items = query_db([1,2,3,4,5,6,7,8,9,0])
    
    # BSON to json VERY IMP
    return json.loads(json_util.dumps(retrieved_items))

def stage3(str, customer_verdict):
    prompt = f"""INSTRUCTION:
    Filter the predicted demand list: {str} to return the most relevant product that matches the customer's demand {customer_verdict}. If no relevant product exists, return an empty list. Exclude any unrelated products. The output should be a valid JSON string in the exact format below, without any additional text or keys:
    {{"products":["product 1", "product 2", ... , "product n"]}}
    RESPONSE(NO PREAMBLE):
    """

    print("\n\n\n",prompt,"\n\n\n")

    response = llm.invoke(prompt)
    try:
        print(response.content)
        json_data =json.loads(response.content)
        return json_data
    except:
        print("invalid json")
        return {"products": []}
    
def LLamaRec(customer_verdict):
    # STAGE 1
    stage1_data = stage1(customer_verdict)
    # stage1_data ={"products": [
    #     "Fanta",
    #     "Sprite",
    #     "Diet Coke"
    # ]}

    # STAGE 2
    stage2_data = stage2(stage1_data["products"])
    filtered_list = []
    # print("lenght ->>>>>>>>>>>>>",len(stage2_data))
    for i in stage2_data:
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print(i["document"]["_id"]["$oid"], i["document"]["name"], i["document"]["image"],end=' \n')

        filtered_data = {
            "id": i["document"]["_id"]["$oid"],
            "name": i["document"]["name"],
            "image": i["document"]["image"],
        }
        
        filtered_list.append(filtered_data)

    str = ""
    for i in filtered_list:
        str = str + "`"+i["name"]+"`,"

    str = str[:len(str)-2]
    # str="`Air Purifier`, `Face Mask`, `Anti-Pollution Nasal Filter`"
    # STAGE 3
    final_products = stage3(str, customer_verdict)
    print(final_products)

    return final_products

# ============================================================== HTTP ROUTES =======================================================================

# Html Routes
@app.route("/", methods=['GET'])
def hello_world():
    data = request.get_json()
    #  TODO: Implementing LLAMA REC HERE
    
    customer_verdict = data["text"]
    response = LLamaRec(customer_verdict)
    if(response):
        return response
    
    return "error"
    

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
    
    file_path = "Data/b296b9db-330d-4617-bacf-1745b6423ead.wav"
    
    # # Speech 2 text
    segments, info = text_model.transcribe(file_path, beam_size=5)
    
    txt = ""

    for segment in segments:
        txt = txt + segment.text

    print(txt)

    # Embedding
    # getEmbedding(txt)

    return "success"
    # LLamaRec
    # stg1 = LlamaRec().firstStage(text)
    # stg2 = LlamaRec().secondStage(stg1)
    # stg3 = LlamaRec().thirdStage(stg2)

    # Save ads to user db(MONGO DB)
    


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