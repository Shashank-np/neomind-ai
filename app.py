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

# ---------------- DARK THEME FIX ----------------
st.markdown("""
<style>

/* REMOVE TOP BAR */
[data-testid="stHeader"] {
    background: transparent;
}

/* MAIN BACKGROUND */
.stApp {
    background: radial-gradient(circle at center, #1b1f2a, #0b0e14);
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #151923, #0b0e14);
}
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {
    background: #374151;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-user"] * {
    color: white !important;
}

/* ASSISTANT MESSAGE (WHITE BOX + WHITE TEXT) */
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: white;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-assistant"] * {
    color: #000000 !important;
    font-weight: 500;
}

/* CHAT INPUT AREA BACKGROUND */
[data-testid="stChatInput"] {
    background: radial-gradient(circle at center, #1b1f2a, #0b0e14);
}

/* CHAT INPUT BOX (WHITE) */
[data-testid="stChatInput"] textarea {
    background: white !important;
    color: black !important;
    border-radius: 30px !important;
    border: 1.5px solid #ef4444 !important;
}

/* SEND BUTTON */
[data-testid="stChatInput"] button {
    background: transparent !important;
    border: none !important;
}

/* BUTTONS */
button {
    background: #0b0e14 !important;
    border: 1px solid #374151 !important;
    color: white !important;
}
button:hover {
    border-color: #ef4444 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- USER LOCATION & TIMEZONE ----------------
def get_user_context():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        timezone = pytz.timezone(res.get("timezone", "UTC"))
        return timezone
    except:
        return pytz.UTC

tz = get_user_context()

# ---------------- SMART LOGIC (UNCHANGED) ----------------
def smart_answer(prompt):
    text = prompt.lower()
    now = datetime.now(tz)

    if "dasara" in text or "dussehra" in text:
        return (
            "Next year’s **Dasara (Dussehra)** date is based on the **Hindu lunar calendar**, "
            "and does **not fall on the same Gregorian date each year**.\n\n"
            "📅 **Saturday, 24 October 2026**"
        )

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow’s date:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"

    if "time" in text:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text or text.strip() == "date":
        return f"📅 **Today’s date:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    if "day" in text:
        return f"📆 **Today is:** {now.strftime('%A')}"

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("🆘 Help & Feedback")
    feedback = st.text_area("Type your feedback here...")

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
    api_key=api_key,
    temperature=temperature,
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh;text-align:center;">
<h1>🧠 NeoMind AI</h1>
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
