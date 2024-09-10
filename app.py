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




app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/save-record": {"origins": "*"}})

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Html Routes
@app.route("/")
def hello_world():
    return "Hello, from Content Ranking Service "

@app.route("/save-record", methods=['POST'])
@cross_origin()
def save_record():

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

    except:
        print("error")

    return "success"





# Socket events ====================================================================================================================================

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