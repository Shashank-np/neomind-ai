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

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>

/* Remove resize arrow + beautify textbox */
textarea {
    width: 100% !important;
    min-height: 90px !important;
    resize: none !important;
    font-size: 16px !important;
    padding: 14px !important;
    border-radius: 10px !important;
    border: 1px solid #e0e0e0 !important;
    background-color: #f9fafb !important;
}

/* Better spacing for labels */
label {
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

/* Audio input styling */
section[data-testid="stAudioInput"] {
    border-radius: 10px;
    background-color: #f9fafb;
    padding: 10px;
    border: 1px solid #e0e0e0;
}

/* Remove Streamlit footer */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

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
st.markdown(
    "<h1 style='text-align:center'>💬 NeoMind AI</h1>",
    unsafe_allow_html=True
)

# ---------------- CHAT INPUT ----------------
prompt = st.text_area(
    "Ask NeoMind AI anything…",
    placeholder="Type your message here…"
)

if prompt:
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

# ---------------- VOICE INPUT ----------------
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

# ---------------- RESPONSE ----------------
if st.session_state.messages:
    last_input = st.session_state.messages[-1].content

    answer = smart_answer(last_input)
    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.markdown(answer)
    st.session_state.messages.append(
        AIMessage(content=answer)
    )
