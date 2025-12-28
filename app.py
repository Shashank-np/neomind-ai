import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import pytz

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- API KEY ----------------
api_key = st.secrets["GROQ_API_KEY"]

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="NeoMind AI", page_icon="🧠", layout="wide")

# ---------------- SKY BLUE UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #e6f7ff, #cceeff);
    animation: bgMove 12s ease infinite;
}
@keyframes bgMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
[data-testid="stSidebar"] {
    background: #d9f0ff;
}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {
    background: #74c0fc;
    color: black;
    border-radius: 16px;
}

/* ASSISTANT MESSAGE BOX */
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: white;
    border-radius: 16px;
}

/* 🔥 FORCE TEXT COLOR (DESKTOP + MOBILE FIX) */
.stChatMessage[data-testid="stChatMessage-assistant"] * {
    color: #003366 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_place" not in st.session_state:
    st.session_state.last_place = None

# ---------------- USER LOCATION & TIMEZONE ----------------
def get_user_context():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        timezone = pytz.timezone(res.get("timezone", "UTC"))
        return timezone
    except:
        return pytz.UTC

tz = get_user_context()

# ---------------- SMART LOCAL LOGIC ----------------
def smart_answer(prompt):
    text = prompt.lower()
    now = datetime.now(tz)

    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text or text.strip() == "date":
        return f"📅 **Today’s date:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow’s date:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"

    if "dasara" in text or "dussehra" in text:
        return (
            "Next year’s **Dasara (Dussehra)** date is based on the **Hindu lunar calendar**, "
            "and does **not fall on the same Gregorian date each year**.\n\n"
            "📅 **Saturday, 24 October 2026**\n\n"
            "This is when it is celebrated in most parts of India."
        )

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_place = None
        st.rerun()

    st.divider()
    st.subheader("🆘 Help & Feedback")

    feedback = st.text_area("Write your message here…")

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

# ---------------- FREE LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=api_key,
    temperature=temperature,
    streaming=False
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
        local = smart_answer(prompt)
        if local:
            answer = local
        else:
            response = llm.invoke(st.session_state.messages)
            answer = response.content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
