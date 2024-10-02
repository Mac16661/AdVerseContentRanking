from faster_whisper import WhisperModel
from functools import lru_cache

@lru_cache(maxsize=1)
class Speech2Text():
    def __init__(self):
        self.model_size = "base"
        self.text_model = WhisperModel(self.model_size,  device="cpu")
        print("Initialized Speech2Text ========================================\n")


    def speech2text(self, file_path):
        segments, info = self.text_model.transcribe(file_path, beam_size=5)
        
        txt = ""

        for segment in segments:
            txt = txt + segment.text

        return txt