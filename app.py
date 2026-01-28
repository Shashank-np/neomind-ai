import streamlit as st
import requests
from datetime import datetime
import pytz
import wikipedia

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

# ---------------- TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5).json()
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

# ---------------- IMAGE DETECTION ----------------
def image_info_response(query):
    if "image" not in query.lower():
        return None

    try:
        wikipedia.set_lang("en")
        topic = query.replace("image", "").strip()
        page = wikipedia.page(topic, auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)

        return f"""
### 🖼️ {page.title}

{summary}

🔗 https://commons.wikimedia.org/wiki/{page.title.replace(" ", "_")}
"""
    except:
        return "⚠️ Please be more specific."

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Your AI Assistant")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------- LLM ----------------
try:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.7
    )
except KeyError:
    st.error("❌ GROQ_API_KEY missing in Streamlit secrets")
    st.stop()

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reply = smart_answer(prompt) or image_info_response(prompt)

        if not reply:
            reply = llm.invoke(st.session_state.messages).content

        st.markdown(reply)
        st.session_state.messages.append(AIMessage(content=reply))
