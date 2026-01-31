import streamlit as st
import requests
from datetime import datetime
import pytz
import hashlib

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

/* Chat bubbles */
section[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 12px;
}

/* Compact voice input */
section[data-testid="stAudioInput"] {
    padding: 4px !important;
    margin: 0 0 6px 0 !important;
    border-radius: 10px;
}

section[data-testid="stAudioInput"] audio {
    height: 26px !important;
}

/* Sticky input area */
.input-zone {
    position: sticky;
    bottom: 0;
    background: white;
    padding-top: 6px;
    z-index: 10;
    border-top: 1px solid #eee;
}

/* Hide footer */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = set()

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

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.processed_audio = set()
        st.rerun()

    st.divider()

    # ---------- FEEDBACK (FIXED) ----------
    st.subheader("🆘 Feedback")

    feedback_text = st.text_area(
        label="Your feedback",
        placeholder="Tell us what you like or what we can improve…",
        height=90
    )

    if st.button("📨 Send Feedback"):
        if feedback_text.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"feedback": feedback_text},
                    timeout=5
                )
                st.success("✅ Thanks for your feedback!")
            except:
                st.error("❌ Failed to send feedback. Try again.")
        else:
            st.warning("⚠️ Please write something before sending.")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center'>💬 NeoMind AI</h1>",
    unsafe_allow_html=True
)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ================= INPUT ZONE =================
st.markdown('<div class="input-zone">', unsafe_allow_html=True)

# ---- Voice input (compact + safe) ----
audio = st.audio_input("🎙️", label_visibility="collapsed")

if audio:
    audio_hash = hashlib.md5(audio.getvalue()).hexdigest()

    if audio_hash not in st.session_state.processed_audio:
        st.session_state.processed_audio.add(audio_hash)

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio) as source:
                audio_data = recognizer.record(source)

            transcript = recognizer.recognize_google(audio_data)

            st.session_state.messages.append(
                HumanMessage(content=transcript)
            )

            answer = smart_answer(transcript)
            if not answer:
                answer = llm.invoke(st.session_state.messages).content

            st.session_state.messages.append(
                AIMessage(content=answer)
            )

            st.rerun()

        except:
            pass  # no repeated error spam

# ---- Text input with arrow ----
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt:
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

    answer = smart_answer(prompt)
    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(
        AIMessage(content=answer)
    )

    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
