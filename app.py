import streamlit as st
import requests
from datetime import datetime
import pytz
import hashlib
import uuid
import tempfile

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
section[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 12px;
}
section[data-testid="stAudioInput"] {
    padding: 4px !important;
    margin: 4px 0 !important;
    border-radius: 10px;
}
section[data-testid="stAudioInput"] audio {
    height: 26px !important;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "voice_error" not in st.session_state:
    st.session_state.voice_error = False

if "audio_key" not in st.session_state:
    st.session_state.audio_key = str(uuid.uuid4())

# ---------------- TIMEZONE ----------------
@st.cache_data(ttl=3600)
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=3).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART ANSWERS ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ Current time: {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 Today: {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- IMAGE MODEL (SAFE LOAD) ----------------
@st.cache_resource
def load_image_model():
    try:
        from ultralytics import YOLO
        return YOLO("yolov8n.pt")
    except Exception as e:
        st.error("Image model failed to load.")
        st.exception(e)
        return None

image_model = load_image_model()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    st.divider()
    st.subheader("🎙️ Voice Input")

    audio = st.audio_input(
        "Speak",
        key=st.session_state.audio_key,
        label_visibility="collapsed"
    )

    if audio:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio) as source:
                audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)

            st.session_state.voice_text = transcript
            st.session_state.voice_error = False
            st.session_state.audio_key = str(uuid.uuid4())
        except:
            st.session_state.voice_error = True

    if st.session_state.voice_error:
        st.warning("Couldn’t understand the voice. Please try again.")

    if st.session_state.voice_text:
        st.success(f"Recognized: {st.session_state.voice_text}")

    # ---------------- IMAGE INPUT ----------------
    st.divider()
    st.subheader("🖼️ Image Input")

    uploaded_image = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )

    st.divider()
    st.subheader("🆘 Feedback")

    feedback = st.text_area(
        "Your feedback",
        placeholder="Tell us what you like or what we can improve…",
        height=90
    )

    if st.button("📨 Send Feedback"):
        if feedback.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"feedback": feedback},
                    timeout=5
                )
                st.success("Thanks for your feedback!")
            except:
                st.error("Failed to send feedback.")
        else:
            st.warning("Please write something first.")

    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt or st.session_state.voice_text:
    user_text = prompt if prompt else st.session_state.voice_text
    st.session_state.voice_text = ""

    st.session_state.messages.append(
        HumanMessage(content=user_text)
    )

    answer = smart_answer(user_text)
    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(
        AIMessage(content=answer)
    )

    st.rerun()

# ---------------- IMAGE PROCESSING ----------------
if uploaded_image and image_model:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_image.read())
        image_path = tmp.name

    results = image_model(image_path)

    detected = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = image_model.names[cls_id]
        detected.append(label)

    detected = list(set(detected))

    if detected:
        reply = "I can see: " + ", ".join(detected)
    else:
        reply = "I couldn't recognize anything in this image."

    st.session_state.messages.append(AIMessage(content=reply))
    with st.chat_message("assistant"):
        st.markdown(reply)
