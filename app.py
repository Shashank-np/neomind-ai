import streamlit as st
import requests
from datetime import datetime
import pytz
import tempfile

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- SAFE gTTS IMPORT ----------------
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ModuleNotFoundError:
    TTS_AVAILABLE = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>
section[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 12px;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}

# ---------------- TIMEZONE (CACHED) ----------------
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
        st.session_state.audio_cache = {}
        st.rerun()

    st.divider()
    st.subheader("🆘 Feedback")

    feedback = st.text_area(
        "Tell us what you think",
        placeholder="Your feedback helps us improve NeoMind AI…",
        height=120
    )

    if st.button("📨 Send Feedback"):
        if feedback.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"feedback": feedback},
                    timeout=5
                )
                st.success("✅ Feedback sent!")
            except:
                st.error("❌ Failed to send feedback")
        else:
            st.warning("⚠️ Please write feedback")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

# ---------------- CHAT HISTORY (FAST) ----------------
for i, msg in enumerate(st.session_state.messages):
    role = "user" if isinstance(msg, HumanMessage) else "assistant"

    with st.chat_message(role):
        st.markdown(msg.content)

        # 🔊 Play cached audio only (NO regeneration)
        if role == "assistant" and i in st.session_state.audio_cache:
            st.audio(st.session_state.audio_cache[i])

# ---------------- CHAT INPUT (WITH ARROW) ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = smart_answer(prompt)
        if not answer:
            answer = llm.invoke(st.session_state.messages).content

        st.markdown(answer)

        # 🔊 Generate TTS ONCE for this message
        if TTS_AVAILABLE:
            tts = gTTS(answer)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name)
                st.session_state.audio_cache[len(st.session_state.messages)] = fp.name
        else:
            st.info("🔊 Voice feature unavailable (gTTS not installed).")

        st.session_state.messages.append(AIMessage(content=answer))
