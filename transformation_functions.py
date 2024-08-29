from openai import OpenAI
import streamlit as st
import base64
import os
import openai
from openai import error

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)


def get_answer(messages):
    system_message = [
        {"role": "system", "content": "Tu es Nora, un psychologue virtuel et assistant en santé mentale. "
         "Tu parles toujours en français et ne dis jamais que tu es un modèle d'IA. "
         "Ton but est d'aider les utilisateurs avec des conseils empathiques, des exercices de pleine conscience, "
         "des stratégies d'adaptation, et des encouragements positifs. Sois toujours bienveillant, empathique, et non-jugemental."
         "tu essaye toujours d'avoir le maximum d'information en posant les bonnes questions, des questions ouverte et très ciblé et engagente pour avoir l'attention de l'utilisateur le maximum possible"
         "si il te demande tu peux l'aider en quoi tu donne des exemples, des problemes personnels? heartbreak? probleme a l entreprise? overwhelming ?"
         }]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content


def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        try:
            # Check if file is too short
            audio_file.seek(0, os.SEEK_END)
            file_size = audio_file.tell()
            if file_size < 100:  # Example threshold for file size in bytes
                raise ValueError("Audio file is too short to process.")
            
            # Reset file pointer
            audio_file.seek(0)
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                response_format="text",
                file=audio_file,
                language="fr"
            )
        except ValueError as e:
            st.warning(str(e))
            return None
        except openai.error.OpenAIError as e:
            st.error(f"An error occurred while processing the audio: {str(e)}")
            return None

    return transcript


def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

