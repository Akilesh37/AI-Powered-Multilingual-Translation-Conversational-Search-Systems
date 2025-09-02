from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from speech_to_text import user_speech_to_text
from voice_recorder import record_until_silence
from text_to_speech import ai_text_to_speech
from file_uploader import upload_to_gdrive
from playsound import playsound
import mysql.connector


# Data Base Connection
db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "transalator_ai"
)
cursor = db.cursor()

# Initialize the LLM
llm = OllamaLLM(model="llama3.2-vision")

# Use ConversationBufferMemory to store the conversation history
memory = ConversationBufferMemory()

# Use LangChain's built-in ConversationChain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True  # Optional: prints internal steps for debugging
)

def handle_conversation():
    print("Welcome to the AI ChatBot! Type 'exit' to quit.")
    
    while True:

        audio_file_user = record_until_silence()
        user_audio_url = upload_to_gdrive(audio_file_user,"user_audio")
        
        text_datas = user_speech_to_text(audio_file_user)
        user_input = text_datas
        if user_input.lower() == "exit":
            break

        response = conversation.predict(input=user_input)
        print("Bot:", response)
        audio_file_bot = ai_text_to_speech(response)
        ai_audio_url = upload_to_gdrive(audio_file_bot,"bot_audio")
        playsound(audio_file_bot)

        user_datas_sst_tts = {'user_id': 2025001,
         'sst_url': user_audio_url,
         'text_data_user': text_datas,
         'text_data_bot': response,
         'tts_url': ai_audio_url}
        
        datas = list(user_datas_sst_tts.values())
        
        insert_query = '''INSERT INTO sst_tts(user_id, sst_url, text_data_user, text_data_bot, tts_url)
                                      values(%s, %s, %s, %s, %s)'''

        cursor.execute(insert_query, datas)
        db.commit()

if __name__ == "__main__":
    handle_conversation()