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
    ASSIST_TEXT = "#000000"   # REQUIRED
    BORDER = "#334155"
    PLACEHOLDER = "#ffffff"
    SEND_BG = "#1e293b"
else:
    BG_MAIN = "#e6f7ff"
    BG_SIDEBAR = "#d9f0ff"
    BG_CARD = "#ffffff"
    TEXT_COLOR = "#000000"
    ASSIST_TEXT = "#000000"   # REQUIRED
    BORDER = "#aaccee"
    PLACEHOLDER = "#5b7fa3"
    SEND_BG = "#ffffff"

# ---------------- FINAL UI ----------------
st.markdown(f"""
<style>

/* REMOVE STREAMLIT TOP/BOTTOM */
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

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: {BG_CARD};
    border-radius: 14px;
}}
.stChatMessage[data-testid="stChatMessage-user"] p,
.stChatMessage[data-testid="stChatMessage-user"] span {{
    color: {TEXT_COLOR} !important;
}}

/* ASSISTANT MESSAGE — FINAL FIX */
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: {BG_CARD};
    border-radius: 14px;
}}

/* Force ALL assistant content colors */
.stChatMessage[data-testid="stChatMessage-assistant"] p,
.stChatMessage[data-testid="stChatMessage-assistant"] span,
.stChatMessage[data-testid="stChatMessage-assistant"] li,
.stChatMessage[data-testid="stChatMessage-assistant"] strong,
.stChatMessage[data-testid="stChatMessage-assistant"] em {{
    color: {ASSIST_TEXT} !important;
}}

/* Code blocks */
.stChatMessage[data-testid="stChatMessage-assistant"] pre,
.stChatMessage[data-testid="stChatMessage-assistant"] code {{
    color: {ASSIST_TEXT} !important;
    background: #f1f5f9 !important;
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
    opacity: 1 !important;
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
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

/* SEND ICON */
[data-testid="stChatInput"] button svg {{
    fill: {TEXT_COLOR} !important;
}}

/* FEEDBACK BOX */
textarea {{
    background: {BG_CARD} !important;
    color: {TEXT_COLOR} !important;
    border: 1px solid {BORDER} !important;
}}

/* BUTTONS */
button {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_COLOR} !important;
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
    text = prompt.lower()
    now = datetime.now(tz)

    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"
    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"
    if "today" in text or text.strip() == "date":
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
