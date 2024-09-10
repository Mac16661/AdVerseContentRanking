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
import uuid
from pydub import AudioSegment
from faster_whisper import WhisperModel
from functools import lru_cache
from langchain_groq import ChatGroq

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/save-record": {"origins": "*"}})

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# ============================================================ UTILITY FUNCTIONS ===================================================================

def saveRecordedFile(request):
# check if the post request has the file part
    print(request.files)
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
    
    file_name = str(uuid.uuid4()) + ".mp3"
    full_file_name = os.path.join("Data", file_name)


    try:
        full_file_name = os.path.join("Data", file_name)
        file.save(full_file_name)
        return full_file_name

    except:
        print("error")

    return "error"

@lru_cache(maxsize=1)
class Speech2Text():
    def __init__(self):
        self.model_size = "tiny.en"
        self. model = WhisperModel(self.model_size,  compute_type="int8")

    def getText(self, path):
        segments, info = self.model.transcribe(path, beam_size=5)

        str = ""

        for segment in segments:
            str = str + segment.text

        print(str)

        return str
    
@lru_cache(maxsize=1)
class LlamaRec():
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key='', 
            model_name="llama-3.1-70b-versatile"
    )
        
    # STAGE 1 [User intrests based on context]
    def firstStage(self, customer_data):
        customer_data = "I like softdrinks"

        promp_ph1 = """
            CUSTOMER Feedback:
            It is cold inside
            INSTRUCTION:
            Return a JSON object with a single key products containing an array of recommended products based on customer data. Omit any additional text or keys. The output should be a valid JSON string in the exact format below:
            {"products":["product 1", "product 2", ... , "product n"]}
            RESPONSE(NO PREAMBLE):
            """

        response = self.llm.invoke(promp_ph1)

        print(response.content)
        # TODO: Should convert string to JSON and return
        return response.content
    
    # Similarity Search[Searching relevant items from DB]
    def secondStage(self, predicted_products):
        # TODO: Interact with VECTOR DB to fetch all similar the ads
        pass 

    # Ranking Retrieved Ads
    def thirdStage(self, retrieved_item):
        prompt_ph2 = """
            INSTRUCTION:
            Filter the predicted demand list: `Heater`, `Thermal Socks`, `Hot Chocolate`, `Electric Blanket` to return the most relevant product that matches the customer's demand `It is really cold inside`. If no relevant product exists, return an empty list. Exclude any unrelated products. The output should be a valid JSON string in the exact format below, without any additional text or keys:
            {"products":["product 1", "product 2", ... , "product n"]}
            RESPONSE(NO PREAMBLE):"""

        # print(promp_ph1)

        response = self.llm.invoke(prompt_ph2)
        print(response.content)
        # TODO: Should convert string to JSON and return
        return response.content
# ============================================================== HTTP ROUTES =======================================================================

# Html Routes
@app.route("/")
def hello_world():
    return "Hello, from Content Ranking Service "

@app.route('/save-record', methods=['POST'])
@cross_origin()
def save_record():

    file_path = saveRecordedFile(request)

    if(file_path == 'error'):
        return "error"
    
    # Speech 2 text
    text = Speech2Text().getText(file_path)
    print(text)

    # LLamaRec
    stg1 = LlamaRec().firstStage(text)
    stg2 = LlamaRec().secondStage(stg1)
    stg3 = LlamaRec().thirdStage(stg2)

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
    print(f"Client connected with socket ID>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  {request.sid}")
    

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected with socket ID >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {request.sid}")



if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, host="0.0.0.0")