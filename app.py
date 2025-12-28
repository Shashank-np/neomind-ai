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

# ---------------- LIGHT SKY-BLUE UI ----------------
st.markdown("""
<style>

/* REMOVE DEFAULT HEADER / FOOTER */
[data-testid="stHeader"],
[data-testid="stBottom"] {
    background: transparent !important;
}

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(180deg, #e6f7ff, #cceeff);
    animation: bgMove 12s ease infinite;
    color: #003366;
}

@keyframes bgMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #d9f0ff;
}
[data-testid="stSidebar"] * {
    color: #003366 !important;
}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {
    background: #bde3ff;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-user"] * {
    color: #003366 !important;
}

/* ASSISTANT MESSAGE */
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: #ffffff;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-assistant"] * {
    color: #003366 !important;
}

/* CHAT INPUT WRAPPER – REMOVE EXTRA WHITE STRIP */
[data-testid="stChatInput"] {
    background: transparent !important;
    padding: 0 !important;
}

/* ===== FIXED INPUT BOX (MATCH FIRST IMAGE) ===== */
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #003366 !important;

    border-radius: 999px !important;          /* pill shape */
    border: 1.5px solid #aaccee !important;   /* single clean border */
    box-shadow: none !important;
    outline: none !important;

    padding: 14px 56px 14px 20px !important;  /* space for arrow */
    min-height: 48px !important;
}

/* REMOVE INNER / DOUBLE BORDER */
[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* PLACEHOLDER */
[data-testid="stChatInput"] textarea::placeholder {
    color: #7aa7c7 !important;
}

/* SEND BUTTON – CLEAN ARROW ONLY */
[data-testid="stChatInput"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 16px !important;
}

/* SEND ARROW ICON */
[data-testid="stChatInput"] button svg {
    fill: #7aa7c7 !important;
    width: 22px !important;
    height: 22px !important;
}

/* GENERAL BUTTONS */
button {
    background: white !important;
    border: 1px solid #aaccee !important;
    color: #003366 !important;
}
button:hover {
    background: #eef7ff !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
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
            answer = llm.invoke(st.session_state.messages).content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
