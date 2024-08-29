from openai import OpenAI
import streamlit as st
import base64
import os
import openai


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
    filter_out_biases_statics = {
        "Merci d'avoir regardé cette vidéo.",
        "Merci d'avoir regardé cette vidéo!",
        "Merci d'avoir regardé cette vidéo !",
        "Merci d'avoir regardé la vidéo.",
        "J'espère que vous avez apprécié la vidéo.",
        "Je vous remercie de vous abonner",
        "Sous-titres réalisés para la communauté d'Amara.org",
        "Merci d'avoir regardé!",
        "❤️ par SousTitreur.com",
        "— Sous-titrage ST'501 —",
        "Thanks for watching!",
        "A bientôt.",
        "À tout à l'heure.",
        "Merci.",
        "Merci et à bientôt."

    }

    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file,
            language="fr"
        )

    # Split the transcript into lines
    transcript_lines = transcript.split('\n')

    # Filter out lines that match any of the phrases
    filtered_transcript_lines = [
        line for line in transcript_lines if line.strip() not in filter_out_biases_statics
    ]

    # Reassemble the filtered transcript
    transcript = '\n'.join(filtered_transcript_lines)

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


