import eventlet

# Monkey patching to make standard library cooperative
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from Helper import TextHandler


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")


# Html Routes
@app.route("/")
def hello_world():
    return "Hello, World! Today"

# Socket events
@socketio.on("audioIn")
def handle_msg(args):
    """
        Takes chunks of audio as inputs, make audio compatible to feed into speech to text model , then convert text to vector embedding, do similar search and return ads

        Args:
            args -> Audio chunks
    """
    handler = TextHandler()
    # Creating new threads for each user audio req
    eventlet.spawn_n(handler.sendResponse, args, request.sid, socketio, eventlet)
    

@socketio.on("connect")
def handle_connect():
    print(f"Client connected with socket ID: {request.sid}")
    

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected with socket ID: {request.sid}")



if __name__ == '__main__':
    socketio.run(app, debug=True)