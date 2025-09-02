from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from langchain.llms import HuggingFacePipeline
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from speech_to_text import user_speech_to_text
from text_to_speech import ai_text_to_speech
from file_uploader import upload_to_gdrive
import mysql.connector

import shutil
import uuid
import os
import base64

# Init app
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static/templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="transalator_ai"
)
cursor = db.cursor()

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import torch

# ✅ Choose an open-access model
model_id = "tiiuae/falcon-7b-instruct"

# ✅ Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

# ✅ Create Hugging Face generation pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.1
)

# ✅ Wrap with LangChain
llm = HuggingFacePipeline(pipeline=pipe)

# ✅ Prompt template
prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are a Best English Teacher, like Tamil to English. Be short and to the point.

{history}
User: {input}
Assistant:"""
)

# ✅ Chat memory
memory = ConversationBufferMemory(memory_key="history")

# ✅ LangChain conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-audio")
async def process_audio(audio: UploadFile = File(...)):
    # Save user audio
    temp_input_path = f"temp_{uuid.uuid4()}.webm"
    with open(temp_input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Speech to text
    user_text = user_speech_to_text(temp_input_path)

    # Get AI response
    bot_response = conversation.predict(input=user_text)

    # Text to speech
    bot_audio_path = ai_text_to_speech(bot_response)

    # Upload to GDrive (optional)
    user_audio_url = upload_to_gdrive(temp_input_path, "user_audio")
    bot_audio_url = upload_to_gdrive(bot_audio_path, "bot_audio")

    # DB log
    values = [2025001, user_audio_url, user_text, bot_response, bot_audio_url]
    cursor.execute(
        '''INSERT INTO sst_tts(user_id, sst_url, text_data_user, text_data_bot, tts_url)
           VALUES (%s, %s, %s, %s, %s)''', values
    )
    db.commit()

    # Convert audio to base64
    with open(bot_audio_path, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode("utf-8")

    return JSONResponse({
        "user_text": user_text,
        "bot_reply": bot_response,
        "audio_base64": audio_base64
    })
