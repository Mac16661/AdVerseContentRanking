from faster_whisper import WhisperModel

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

model_size = "base"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cpu")

segments, info = model.transcribe("1-first-snowfall.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
str=""
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    str = str + segment.text