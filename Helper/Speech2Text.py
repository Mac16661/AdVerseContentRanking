from faster_whisper import WhisperModel
from functools import lru_cache

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