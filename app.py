import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="""
You are NeoMind AI.
You talk like a friendly human.
You NEVER say you are a language model.
Keep responses simple and natural.
""")
    ]

# ---------------- FIXED LIGHT THEME COLORS ----------------
BG_MAIN = "#e6f7ff"
BG_SIDEBAR = "#f4faff"
BG_CARD = "#ffffff"
TEXT_COLOR = "#000000"
BORDER = "#aaccee"
PLACEHOLDER = "#5b7fa3"
SEND_BG = "#ffffff"

# ---------------- CSS ----------------
# st.markdown(f"""
# <style>
# [data-testid="stHeader"], [data-testid="stBottom"] {{
#     background: transparent !important;
# }}

# .stApp {{
#     background: {BG_MAIN};
#     color: {TEXT_COLOR};
# }}

# [data-testid="stSidebar"] {{
#     background: {BG_SIDEBAR};
# }}
# [data-testid="stSidebar"] * {{
#     color: {TEXT_COLOR};
# }}

# .stChatMessage {{
#     background: {BG_CARD};
#     border-radius: 14px;
# }}

# .stChatMessage * {{
#     color: {TEXT_COLOR};
# }}

# [data-testid="stChatInput"] textarea {{
#     background: {BG_CARD};
#     color: {TEXT_COLOR};
#     border-radius: 999px;
#     border: 1.5px solid {BORDER};
#     padding: 14px 64px 14px 20px;
# }}

# [data-testid="stChatInput"] textarea::placeholder {{
#     color: {PLACEHOLDER};
# }}

# [data-testid="stChatInput"] button {{
#     position: absolute;
#     right: 12px;
#     top: 50%;
#     transform: translateY(-50%);
#     background: {SEND_BG};
#     border: 1px solid {BORDER};
#     border-radius: 50%;
#     width: 38px;
#     height: 38px;
# }}

# [data-testid="stChatInput"] button svg {{
#     fill: {TEXT_COLOR};
# }}
# </style>
# """, unsafe_allow_html=False)

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
    now = datetime.today().astimezone(tz)

    if text in ["hi", "hello", "hey", "hai"]:
        return "Hey 👋 How can I help you today?"

    if text in ["time", "what is time", "what's time", "current time", "what is the time"]:
        return f"⏰ **{now.strftime('%I:%M %p')}**"

    if "your name" in text:
        return "I’m **NeoMind AI** 🙂"

    if "creator full name" in text:
        return "**Shashank N P**"

    if "creator" in text:
        return "**Shashank**"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **{tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})**"

    if text == "today" or text == "date":
        return f"📅 **{now.strftime('%d %B %Y')} ({now.strftime('%A')})**"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

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
if len(st.session_state.messages) == 1:
    st.markdown("""
    <div style="margin-top:30vh;text-align:center;">
        <h1>💬 NeoMind AI</h1>
        <p>Ask. Think. Generate.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages[1:]:
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



