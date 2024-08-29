import streamlit as st
import os
from transformation_functions import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from langchain_community.llms import OpenAI
import tempfile
import openai
import langchain
# ==================================================
#                     SET UP VARIABLES
# ==================================================
LANGCHAIN_TRACING_V2 = True
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = st.secrets.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "NoraVoiceBot"
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

llm = OpenAI(temperature=0)

st.set_page_config(
    page_title="Nora",
    page_icon="🧠",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Premier test avec Whisper, OpenAI TTS text to voice chatbot. N'hésitez pas à l'essayer et à m'envoyer vos commentaires à badreddine.saadioui@incenteev.com."
    }
)


# ==================================================
#          Session State Initialization
# ==================================================
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_topic" not in st.session_state:
        st.session_state.user_topic = ""
    if "setup_complete" not in st.session_state:
        st.session_state.setup_complete = False


initialize_session_state()


# ==================================================
#               Home page setup
# ==================================================
st.title("Nora experte en Santé Mentale💆‍♂️")
if not st.session_state.setup_complete:
    st.subheader("Bienvenue! 😊")
    st.markdown(
        """
        Je suis Nora, psychologue et experte en santé mentale. Je suis là pour vous offrir un espace sûr pour parler de vos préoccupations afin d'explorer des techniques de bien-être ou simplement discuter de ce qui vous pèse.

        Pour commencer, veuillez me donner quelque info d'abord.
        """)

    st.session_state.user_name = st.text_input(
        "Quel est votre nom?", value=st.session_state.user_name)
    st.session_state.user_topic = st.text_input(
        "De quoi souhaitez-vous parler aujourd'hui?", value=st.session_state.user_topic)

    if st.button("Allons-y"):
        if st.session_state.user_name and st.session_state.user_topic:
            st.session_state.setup_complete = True
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Bonjour {st.session_state.user_name}! Vous souhaitez parler de {st.session_state.user_topic}. Comment puis-je vous aider?"})
            st.balloons()
            st.rerun()

        else:
            st.warning(
                "Veuillez remplir votre nom et le sujet de la conversation.")


# ==================================================
#          Main conversation interface
# ==================================================
else:
    st.sidebar.title(f"Bonjour {st.session_state.user_name} !👋🏻")
    st.sidebar.subheader(f"Vous avez choisi {
                         st.session_state.user_topic} comme sujet")
    st.sidebar.markdown("### Comment commencer la séance ?")
    st.sidebar.markdown(
        """
        Pour démarrer une conversation avec Nora, cliquez sur l'icône du micro 🎙️ en bas de la page. 
        Nora enregistrera automatiquement ce que vous dites, le transcrira et vous répondra instantanément.
        
        **Conseils :**
        - Parlez clairement pour de meilleurs résultats de transcription.
        - Soyez précis sur le sujet que vous souhaitez aborder pour des réponses plus adaptées.
        
        N'hésitez pas à tester toutes les capacités de Nora. Jouez avec et explorez ses fonctionnalités au maximum ! 😊

        **Votre Feedback est précieux !**
        - Partagez vos impressions et suggestions pour améliorer l'expérience avec Nora.
        - Envoyez vos retours à [badreddine.saadioui@incenteev.com](mailto:badreddine.saadioui@incenteev.com)
        """
    )
    st.sidebar.markdown("### Citation du Jour")
    st.sidebar.markdown(
        "> *La plus grande gloire n'est pas de ne jamais tomber, mais de se relever à chaque chute.* - Nelson Mandela")

    # Footer and Audio Recorder Setup
    footer_container = st.container()
    with footer_container:
        # Idk how to center the icon xD so i did this setup, if it works don't touch it literally
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            audio_bytes = audio_recorder(
                text="Cliquez et exprimez vous",
            )

    # Display conversation history
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="👩🏻‍⚕️"):
                st.write(message["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])

    # Process audio input and convert to text
    if audio_bytes:
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        # Ensure the file is not too short
        if os.path.getsize(webm_file_path) < 100:
            st.warning("L'audio est très court.")
        else:

            with st.spinner("👂..."):
                transcript = speech_to_text(webm_file_path)

            if transcript:
                st.session_state.messages.append(
                    {"role": "user", "content": transcript})
                with st.chat_message("user", avatar="👤"):
                    st.write(transcript)
                os.remove(webm_file_path)
            else:
                st.warning(
                    "Unable to transcribe the audio. Please try again.")

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="👩🏻‍⚕️"):
            with st.spinner("🤔..."):
                final_response = get_answer(st.session_state.messages)
            with st.spinner("🤔..."):
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            st.write(final_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": final_response})
            os.remove(audio_file)

    footer_container.float("bottom: 3rem;")
