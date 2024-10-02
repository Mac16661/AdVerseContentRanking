import eventlet
from eventlet import wsgi

# Monkey patching to make standard library cooperative
eventlet.monkey_patch()

from flask import Flask, request
from flask_cors import CORS, cross_origin
from Helper import AudioHandler
from flask import Flask, copy_current_request_context
from dotenv import load_dotenv
load_dotenv()

from Helper import AudioHandler


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins":  ["*"]}})
CORS(app, resources={r"/text-to-embedding": {"origins": "*"}})
CORS(app, resources={r"/save-record-web-beta": {"origins": "*"}})


# # Html Routes
@app.route("/", methods=['GET'])
def hello_world():
    return "Hello"


@app.route('/save-record-web-beta', methods=['POST'])
@cross_origin()
def save_record_v2():
    handler = AudioHandler()

    @copy_current_request_context
    def handle_audio_in_thread():
        return handler.handleAudio(request)


    try:
        # Spawn a new green thread to handle audio processing
        response = eventlet.spawn(handle_audio_in_thread)

        # Wait for the response and return it
        return response.wait()  # This returns the result of handleAudio
    except Exception as e:
        # Log the error and return an appropriate response
        print(f"Error handling audio: {str(e)}")
        return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    # socketio.run(app, debug=False, port=5000, host="0.0.0.0")
    print(eventlet.__version__)
    wsgi.server(eventlet.listen(('localhost', 5000)), app)