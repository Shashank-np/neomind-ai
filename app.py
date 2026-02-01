import streamlit as st
import uuid
import speech_recognition as sr

st.set_page_config(page_title="Voice Recognition Test", layout="centered")

# ---------------- SESSION STATE ----------------
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "voice_error" not in st.session_state:
    st.session_state.voice_error = False

if "audio_key" not in st.session_state:
    st.session_state.audio_key = str(uuid.uuid4())

# ---------------- UI ----------------
st.title("🎙️ Voice Recognition")

audio = st.audio_input(
    "Speak now",
    key=st.session_state.audio_key,
    label_visibility="collapsed"
)

# ---------------- VOICE PROCESS ----------------
if audio:
    try:
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        # ✅ success
        st.session_state.voice_text = text
        st.session_state.voice_error = False

        # reset mic
        st.session_state.audio_key = str(uuid.uuid4())

    except:
        st.session_state.voice_error = True
        st.session_state.voice_text = ""

# ---------------- OUTPUT ----------------
if st.session_state.voice_text:
    st.success(f"Recognized text: {st.session_state.voice_text}")

if st.session_state.voice_error:
    st.warning("Could not understand the voice. Please try again.")
