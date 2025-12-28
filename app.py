import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import pytz
import random

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="NeoMind AI", page_icon="🌙", layout="wide")

# ---------------- NIGHT SKY + STARS ----------------
stars = "".join(
    f"<span class='star' style='top:{random.randint(0,100)}%;left:{random.randint(0,100)}%;animation-delay:{random.random()*5}s'></span>"
    for _ in range(80)
)

st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(180deg, #050b2e, #020617);
    color: white;
    overflow: hidden;
}}

.star {{
    position: fixed;
    width: 2px;
    height: 2px;
    background: white;
    border-radius: 50%;
    opacity: 0.8;
    animation: twinkle 3s infinite ease-in-out;
}}

@keyframes twinkle {{
    0% {{ opacity: 0.2; }}
    50% {{ opacity: 1; }}
    100% {{ opacity: 0.2; }}
}}

[data-testid="stSidebar"] {{
    background: #020617;
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: #1e293b;
    color: white;
    border-radius: 14px;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: #020617;
    color: #e5e7eb;
    border-radius: 14px;
}}
</style>
{stars}
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- USER LOCATION & TIMEZONE ----------------
def get_user_timezone():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_user_timezone()

# ---------------- SMART DATE & TIME ----------------
def date_time_answer(prompt):
    text = prompt.lower()
    now = datetime.now(tz)

    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 **Today’s date:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow’s date:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"

    if "yesterday" in text:
        yest = now - timedelta(days=1)
        return f"📅 **Yesterday’s date:** {yest.strftime('%d %B %Y')} ({yest.strftime('%A')})"

    if "date" in text:
        return f"📅 **Today’s date:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    if "day" in text:
        return f"📆 **Today is:** {now.strftime('%A')}"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌙 NeoMind AI")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.5)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- FREE LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh;text-align:center;">
<h1>🌌 NeoMind AI</h1>
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
        local = date_time_answer(prompt)

        if local:
            answer = local
        else:
            response = llm.invoke(st.session_state.messages)
            answer = response.content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
