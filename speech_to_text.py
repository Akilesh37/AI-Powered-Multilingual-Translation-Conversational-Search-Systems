# !nvidia-smi

#! pip install git+https://github.com/openai/whisper.git -q

import whisper
from IPython.display import Audio, display

model = whisper.load_model("medium") #769M Parameter

def user_speech_to_text(audio):

    display(Audio(audio))

    result = model.transcribe(audio)
    return result["text"]

