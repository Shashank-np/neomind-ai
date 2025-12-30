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
    BG_MAIN = "#0b1220"
    BG_SIDEBAR = "#020617"
    BG_CARD = "#020617"
    TEXT_COLOR = "#ffffff"
    ASSIST_TEXT = "#e5e7eb"
    BORDER = "#334155"
    PLACEHOLDER = "#cbd5f5"
    SEND_BG = "#1e293b"
    CODE_BG = "#020617"
    CODE_TEXT = "#e5e7eb"
else:
    BG_MAIN = "#e6f7ff"
    BG_SIDEBAR = "#d9f0ff"
    BG_CARD = "#ffffff"
    TEXT_COLOR = "#000000"
    ASSIST_TEXT = "#0f172a"
    BORDER = "#aaccee"
    PLACEHOLDER = "#5b7fa3"
    SEND_BG = "#ffffff"
    CODE_BG = "#f8fafc"
    CODE_TEXT = "#020617"

# ---------------- FINAL UI (MOBILE + DESKTOP FIX) ----------------
st.markdown(f"""
<style>

/* REMOVE STREAMLIT HEADER/FOOTER */
[data-testid="stHeader"],
[data-testid="stBottom"] {{
    display: none;
}}

/* MAIN */
.stApp {{
    background: {BG_MAIN};
    color: {TEXT_COLOR};
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT_COLOR};
}}

/* CHAT WRAPPER – FIX MOBILE SPACING */
.block-container {{
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: {BG_CARD};
    border-radius: 16px;
}}
.stChatMessage[data-testid="stChatMessage-user"] * {{
    color: {TEXT_COLOR};
}}

/* ASSISTANT MESSAGE */
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: {BG_CARD};
    border-radius: 16px;
}}
.stChatMessage[data-testid="stChatMessage-assistant"] .stMarkdown,
.stChatMessage[data-testid="stChatMessage-assistant"] .stMarkdown * {{
    color: {ASSIST_TEXT} !important;
    opacity: 1 !important;
}}

/* CODE BLOCKS */
.stChatMessage[data-testid="stChatMessage-assistant"] pre {{
    background: {CODE_BG} !important;
    color: {CODE_TEXT} !important;
    border-radius: 14px;
    padding: 14px;
}}
.stChatMessage[data-testid="stChatMessage-assistant"] code {{
    color: {CODE_TEXT} !important;
}}

/* CHAT INPUT */
[data-testid="stChatInput"] textarea {{
    background: {BG_CARD};
    color: {TEXT_COLOR};
    border-radius: 999px;
    border: 1.5px solid {BORDER};
    padding: 14px 64px 14px 20px;
}}

/* PLACEHOLDER */
[data-testid="stChatInput"] textarea::placeholder {{
    color: {PLACEHOLDER};
}}

/* SEND BUTTON */
[data-testid="stChatInput"] button {{
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: {SEND_BG};
    border: 1px solid {BORDER};
    border-radius: 50%;
    width: 38px;
    height: 38px;
}}

/* SEND ICON */
[data-testid="stChatInput"] button svg {{
    fill: {TEXT_COLOR};
}}

</style>
""", unsafe_allow_html=True)

# ---------------- USER TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART LOGIC ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if "your name" in text:
        return "**Rossie**"

    if "creator" in text or "who created" in text or "creator name" in text:
        return "**Shashank N P**"

    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"

    if "today" in text or text == "date":
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        st.toggle("🌙 Dark Mode", key="dark_mode")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:28vh;text-align:center;">
<h1>💬 NeoMind AI</h1>
<p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages:
    with st.chat_message("user" if isinstance(m, HumanMessage) else "assistant"):
        st.markdown(m.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = smart_answer(prompt) or llm.invoke(st.session_state.messages).content
        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
