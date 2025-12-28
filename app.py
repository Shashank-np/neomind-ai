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

# ---------------- FINAL DARK UI (CHATBOX FIXED) ----------------
st.markdown("""
<style>

/* REMOVE STREAMLIT HEADER & FOOTER WHITE AREAS */
[data-testid="stHeader"],
[data-testid="stBottom"] {
    background: transparent !important;
}

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b0e14, #1b1f2a);
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0e14, #151923);
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* USER MESSAGE */
.stChatMessage[data-testid="stChatMessage-user"] {
    background: #6b7280;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-user"] * {
    color: white !important;
}

/* ASSISTANT MESSAGE */
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: #111827;
    border-radius: 14px;
}
.stChatMessage[data-testid="stChatMessage-assistant"] * {
    color: white !important;
    font-weight: 500;
}

/* ---------------- CHAT INPUT FIX ---------------- */

/* REMOVE WHITE BACKGROUND BEHIND CHAT INPUT */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    background: transparent !important;
}

/* CHAT INPUT BOX (ONLY THIS IS WHITE) */
[data-testid="stChatInput"] textarea {
    background: white !important;
    color: black !important;
    border-radius: 28px !important;
    border: 2px solid #ef4444 !important;
    padding: 14px 52px 14px 18px !important;
    box-shadow: none !important;
}

/* REMOVE DOUBLE BORDER */
[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* PLACEHOLDER */
[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
}

/* SEND BUTTON – BLACK */
[data-testid="stChatInput"] button {
    background: black !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    margin-right: 8px !important;
    border: none !important;
}

/* SEND ARROW – WHITE */
[data-testid="stChatInput"] button svg {
    fill: white !important;
}

/* GENERAL BUTTONS */
button {
    background: transparent !important;
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

# ---------------- USER TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART LOGIC (UNCHANGED) ----------------
def smart_answer(prompt):
    text = prompt.lower()
    now = datetime.now(tz)

    if "dasara" in text or "dussehra" in text:
        return (
            "Next year’s **Dasara (Dussehra)** date is based on the **Hindu lunar calendar**.\n\n"
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

    temperature = st.slider("Creativity", 0.0, 1.0, 0.5)

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
    api_key=st.secrets["GROQ_API_KEY"],
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
