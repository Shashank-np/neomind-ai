import streamlit as st
import requests
from datetime import datetime
import pytz
import uuid
import base64
import json

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
/* Chat */
section[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 12px;
}

/* Compact sidebar inputs */
.small-label label {
    font-size: 13px !important;
}
section[data-testid="stAudioInput"] {
    padding: 2px !important;
}
section[data-testid="stFileUploader"] {
    padding: 2px !important;
}
section[data-testid="stAudioInput"] audio {
    height: 24px !important;
}

/* Sticky footer text */
.sidebar-footer {
    position: sticky;
    bottom: 0;
    background: #f8f9fa;
    padding-top: 8px;
    font-size: 12px;
    color: #666;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

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

    if text in ["time", "current time"]:
        return f"⏰ Current time: {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 Today: {now.strftime('%d %B %Y')}"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    st.divider()

    # -------- VOICE INPUT --------
    st.markdown("**🎙 Voice Input**", unsafe_allow_html=True)

    audio = st.audio_input(
        "voice",
        key=st.session_state.audio_key,
        label_visibility="collapsed"
    )

    if audio:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(audio) as source:
                data = r.record(source)

            st.session_state.voice_text = r.recognize_google(data)
            st.session_state.audio_key = str(uuid.uuid4())
        except:
            st.warning("Could not understand voice. Try again.")

    if st.session_state.voice_text:
        st.success(f"Recognized: {st.session_state.voice_text}")

    # -------- IMAGE INPUT --------
    st.divider()
    st.markdown("**🖼 Image Input**")

    image_file = st.file_uploader(
        "image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

    # -------- FEEDBACK --------
    st.divider()
    st.markdown("**🆘 Feedback**")

    feedback = st.text_area(
        "feedback",
        placeholder="Tell us what we can improve…",
        height=70,
        label_visibility="collapsed"
    )

    if st.button("📨 Send Feedback"):
        if feedback.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={"feedback": feedback}
            )
            st.success("Thanks for your feedback!")

    st.markdown(
        "<div class='sidebar-footer'>Created by <b>Shashank N P</b></div>",
        unsafe_allow_html=True
    )

# ---------------- TEXT LLM ----------------
text_llm = ChatGroq(
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

# ---------------- IMAGE RECOGNITION (FIXED) ----------------
if image_file:
    img_bytes = image_file.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode()

    with st.chat_message("user"):
        st.image(image_file, caption="Uploaded Image", use_container_width=True)

    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    }

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    description = res.json()["choices"][0]["message"]["content"]

    st.session_state.messages.append(AIMessage(content=description))

    with st.chat_message("assistant"):
        st.markdown(description)

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt or st.session_state.voice_text:
    user_text = prompt if prompt else st.session_state.voice_text
    st.session_state.voice_text = ""

    st.session_state.messages.append(HumanMessage(content=user_text))

    answer = smart_answer(user_text)
    if not answer:
        answer = text_llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(AIMessage(content=answer))
    st.rerun()
