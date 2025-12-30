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

# ---------------- FINAL UI FIX ----------------
st.markdown(f"""
<style>

/* REMOVE STREAMLIT DEFAULT BARS */
[data-testid="stHeader"],
[data-testid="stBottom"] {{
    background: transparent !important;
}}

/* MAIN BACKGROUND */
.stApp {{
    background: {BG_MAIN};
    color: {TEXT_COLOR} !important;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT_COLOR} !important;
}}

/* CHAT BUBBLES */
.stChatMessage {{
    background: {BG_CARD};
    border-radius: 14px;
}}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] * {{
    color: {TEXT_COLOR} !important;
}}

/* ASSISTANT TEXT */
.assistant-text {{
    color: {TEXT_COLOR} !important;
    opacity: 1 !important;
    line-height: 1.6;
    font-size: 16px;
}}

/* ASSISTANT CODE BLOCKS */
.assistant-text pre {{
    background: #ffffff !important;
    color: #000000 !important;
    padding: 14px !important;
    border-radius: 12px !important;
    overflow-x: auto !important;
}}

/* INLINE CODE */
.assistant-text code {{
    background: #f1f5f9 !important;
    color: #000000 !important;
    padding: 2px 6px;
    border-radius: 6px;
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
    color: {PLACEHOLDER} !important;
}}

/* SEND BUTTON */
[data-testid="stChatInput"] button {{
    position: absolute !important;
    right: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    background: {SEND_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
}}

/* SEND ICON */
[data-testid="stChatInput"] button svg {{
    fill: {TEXT_COLOR} !important;
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

    if "creator full name" in text:
        return "**Shashank N P**"
    if "creator" in text:
        return "**Shashank**"
    if "your name" in text:
        return "**Rossie**"
    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"
    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"
    if "today" in text:
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

    # ✅ FEEDBACK BOX ADDED
    st.divider()
    st.subheader("🆘 Help & Feedback")

    feedback = st.text_area("Share your feedback or suggestions")
    if st.button("Send Feedback"):
        if feedback.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={"message": feedback},
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")

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
<div style="margin-top:30vh;text-align:center;">
<h1>💬 NeoMind AI</h1>
<p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages:
    with st.chat_message("user" if isinstance(m, HumanMessage) else "assistant"):
        if isinstance(m, AIMessage):
            st.markdown(
                f"<div class='assistant-text'>{m.content}</div>",
                unsafe_allow_html=True
            )
        else:
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
        st.session_state.messages.append(AIMessage(content=answer))
        st.markdown(
            f"<div class='assistant-text'>{answer}</div>",
            unsafe_allow_html=True
        )
