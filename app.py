import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------- THEME COLORS ----------------
if st.session_state.dark_mode:
    BG_MAIN = "#0f172a"
    BG_SIDEBAR = "#020617"
    BG_CARD = "#020617"
    TEXT_COLOR = "#ffffff"
    BORDER = "#334155"
    PLACEHOLDER = "#ffffff"
    SEND_BG = "#1e293b"
else:
    BG_MAIN = "#e6f7ff"
    BG_SIDEBAR = "#d9f0ff"
    BG_CARD = "#ffffff"
    TEXT_COLOR = "#000000"
    BORDER = "#aaccee"
    PLACEHOLDER = "#5b7fa3"
    SEND_BG = "#ffffff"

# ---------------- FINAL UI ----------------
st.markdown(f"""
<style>

/* MAIN BACKGROUND */
.stApp {{
    background: {BG_MAIN};
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT_COLOR} !important;
}}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: {BG_CARD};
    border-radius: 14px;
}}
.stChatMessage[data-testid="stChatMessage-user"] * {{
    color: {TEXT_COLOR} !important;
}}

/* ASSISTANT MESSAGE BOX */
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: {BG_CARD};
    border-radius: 14px;
}}

/* 🔥 THIS IS THE FIX — STREAMLIT CANNOT OVERRIDE THIS */
.assistant-text {{
    color: #ffffff !important;
    opacity: 1 !important;
    font-size: 16px;
    line-height: 1.6;
}}

/* CODE BLOCKS */
.assistant-text pre {{
    background: #ffffff !important;
    color: #000000 !important;
    border-radius: 12px;
    padding: 12px;
}}

.assistant-text code {{
    color: #000000 !important;
}}

/* CHAT INPUT */
[data-testid="stChatInput"] textarea {{
    background: {BG_CARD};
    color: {TEXT_COLOR};
    border-radius: 999px;
    border: 1.5px solid {BORDER};
}}

/* SEND BUTTON */
[data-testid="stChatInput"] button svg {{
    fill: {TEXT_COLOR};
}}

</style>
""", unsafe_allow_html=True)

# ---------------- TIMEZONE ----------------
def get_timezone():
    try:
        return pytz.timezone(
            requests.get("https://ipapi.co/json/").json().get("timezone", "UTC")
        )
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART LOGIC ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if "creator full name" in text:
        return "Shashank N P"
    if "creator" in text:
        return "Shashank"
    if "your name" in text:
        return "Rossie"
    if "time" in text:
        return now.strftime("%I:%M %p")
    if "today" in text:
        return now.strftime("%d %B %Y")

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.toggle("🌙 Dark Mode", key="dark_mode")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages:
    with st.chat_message("user" if isinstance(m, HumanMessage) else "assistant"):
        st.markdown(
            f"<div class='assistant-text'>{m.content}</div>",
            unsafe_allow_html=True
        )

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = smart_answer(prompt) or llm.invoke(st.session_state.messages).content
        st.markdown(
            f"<div class='assistant-text'>{answer}</div>",
            unsafe_allow_html=True
        )
        st.session_state.messages.append(AIMessage(content=answer))
