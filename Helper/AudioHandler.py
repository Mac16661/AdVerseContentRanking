import uuid
import os
from functools import lru_cache
from .Speech2Text import Speech2Text
from .LlamaRec import LLMContentRanking

@lru_cache(maxsize=1)
class AudioHandler():
    def __init__(self):
        print("Initialized Audio Handler ========================================\n")
    
    def saveRecordedFile(self, request):
        if 'file' not in request.files:
            print("No audio file in req ")
            return "error"
        
        file = request.files['file']

        if file.filename == '':
            print("No file name")
            return "error"
        
        file_name = str(uuid.uuid4()) + ".wav"
    
        try:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "Data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)  

            # Create the full path for the file
            full_file_name = os.path.join(data_dir, file_name)
            print(f"Saving file to: {full_file_name}")

            # Save the file
            file.save(full_file_name)
            return full_file_name

        except Exception as e:
            print("error occurred while saving -> ", e)

        return "error"
    
    # TODO: Handle audio
    def handleAudio(self, request):

        # Save audio and returns path
        file_path = self.saveRecordedFile(request)
        print(file_path)
        if(file_path == 'error'):
            return "error"
    
        # Speech 2 text
        customer_data = Speech2Text().speech2text(file_path)
        if(len(customer_data)<1):
            print(customer_data)
            return []
        print("Speech 2 text -> ",customer_data)

        response = LLMContentRanking().LLamaRec(customer_data)
        return response

    

    