from gtts import gTTS
from playsound import playsound
from datetime import datetime
import os
import streamlit as st


def ai_text_to_speech(text_data):
    tts = gTTS(text_data, lang="ta")
    file_name = f"ai_text_audio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    tts.save(file_name)
    return file_name