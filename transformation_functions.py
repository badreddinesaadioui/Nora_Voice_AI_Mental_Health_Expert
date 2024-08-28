from openai import OpenAI
import streamlit as st
import base64

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)


def get_answer(messages):
    system_message = [
        {"role": "system", "content": "Tu es Nora, un psychologue virtuel et assistant en santé mentale. "
         "Tu parles toujours en français et ne dis jamais que tu es un modèle d'IA. "
         "Ton but est d'aider les utilisateurs avec des conseils empathiques, des exercices de pleine conscience, "
         "des stratégies d'adaptation, et des encouragements positifs. Sois toujours bienveillant, empathique, et non-jugemental. "
         "Tu essayes toujours d'obtenir le maximum d'informations en posant des questions ouvertes, ciblées et engageantes pour retenir l'attention de l'utilisateur le plus longtemps possible. "
         "Tu peux utiliser des expressions naturelles comme 'euh', 'umh', et même rire ou sourire légèrement lorsque cela est approprié, pour rendre la conversation plus humaine et authentique. "
         "Si on te demande comment tu peux aider, tu donnes des exemples tels que des problèmes personnels, des peines de cœur, des problèmes au travail, ou un sentiment de débordement."
         }]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content


def speech_to_text(audio_data):
    try:
        with open(audio_data, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                response_format="text",
                file=audio_file,
                language="fr"
            )
        return transcript
    except openai.error.OpenAIError as e:
        # Log the error or print it to the console for debugging purposes
        print(f"An error occurred: {e}")
        # Show a user-friendly message in French
        st.warning("Il y a eu un problème lors du traitement de votre demande. Veuillez ré-enregistrer l'audio, s'il vous plaît.")
        # Return None to indicate failure
        return None



def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text,
        speed=1
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
