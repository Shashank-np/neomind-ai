import streamlit as st
import requests
from datetime import datetime
import pytz

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

st.toast("NeoMind AI is ready 🎙️", icon="🧠")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- TIMEZONE (CACHED) ----------------
@st.cache_data(ttl=3600)
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=3).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

if "tz" not in st.session_state:
    st.session_state.tz = get_timezone()

tz = st.session_state.tz

# ---------------- SMART ANSWERS ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # -------- FEEDBACK BOX --------
    st.subheader("🆘 Feedback")

    feedback_text = st.text_area(
        "Tell us what you think",
        placeholder="Your feedback helps us improve NeoMind AI…",
        height=120
    )

    if st.button("📨 Send Feedback"):
        if feedback_text.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"feedback": feedback_text},
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

# ---------------- UI HEADER ----------------
st.markdown(
    "<h1 style='text-align:center'>💬 NeoMind AI</h1>",
    unsafe_allow_html=True
)

# ---------------- INPUT STYLE FIX ----------------
st.markdown("""
<style>
textarea {
    width: 100% !important;
    min-height: 70px !important;
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TEXT INPUT (FIXED SIZE) ----------------
prompt = st.text_area(
    "Ask NeoMind AI anything...",
    placeholder="Type your message here…",
    height=70
)

if prompt:
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

# ---------------- 🎙️ LIVE MIC INPUT ----------------
st.markdown("### 🎙️ Voice Input")

audio_bytes = st.audio_input("Click mic and speak")

if audio_bytes:
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_bytes) as source:
            audio_data = recognizer.record(source)

        transcript = recognizer.recognize_google(audio_data)

        st.success(f"You said: {transcript}")

        st.session_state.messages.append(
            HumanMessage(content=transcript)
        )

    except:
        st.error("Sorry, I couldn't understand your voice.")

# ---------------- CHAT RESPONSE ----------------
if st.session_state.messages:
    last_input = st.session_state.messages[-1].content

    answer = smart_answer(last_input)

    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.markdown(answer)
    st.session_state.messages.append(
        AIMessage(content=answer)
    )
