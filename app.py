import streamlit as st
import requests
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------- API KEY ----------------
api_key = st.secrets["GROQ_API_KEY"]

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_added" not in st.session_state:
    st.session_state.system_added = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
        st.rerun()

    st.divider()
    st.subheader("🆘 Help & Feedback")

    feedback = st.text_area("Write your message here…")

    if st.button("Send Feedback"):
        if feedback.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={
                    "name": "NeoMind AI User",
                    "email": "no-reply@neomind.ai",
                    "message": feedback
                }
            )
            st.success("✅ Feedback sent!")
        else:
            st.warning("Please write something")

    st.caption("Created by **Shashank N P**")

# ---------------- CLEAN CHAT INPUT CSS (FINAL FIX) ----------------
st.markdown("""
<style>

/* REMOVE BACK FRAME */
[data-testid="stChatInput"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 12px !important;
}

/* MAIN INPUT */
[data-testid="stChatInput"] textarea {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    border-radius: 28px !important;
    padding: 14px 52px 14px 20px !important;
    font-size: 16px !important;
    min-height: 52px !important;
    resize: none !important;
}

/* PLACEHOLDER */
[data-testid="stChatInput"] textarea::placeholder {
    color: #bbbbbb !important;
}

/* SEND BUTTON — KEEP STREAMLIT BEHAVIOR */
[data-testid="stChatInput"] button {
    background-color: #000000 !important;
    border: 2px solid #ffffff !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    margin-bottom: 6px !important;
}

/* MOBILE RESPONSIVE */
@media (max-width: 768px) {
    [data-testid="stChatInput"] textarea {
        font-size: 15px !important;
        padding: 12px 48px 12px 18px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- CITY DATA ----------------
BAR_DATA = {
    "bengaluru": [
        "Toit – Indiranagar",
        "Big Pitcher – Indiranagar",
        "The Biere Club – Lavelle Road",
        "Skyye – UB City",
        "Drunken Daddy – Koramangala"
    ],
    "bangalore": [
        "Toit – Indiranagar",
        "Big Pitcher – Indiranagar",
        "The Biere Club – Lavelle Road",
        "Skyye – UB City",
        "Drunken Daddy – Koramangala"
    ]
}

# ---------------- SMART ANSWER ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    if "bar" not in text:
        return None

    now = datetime.now().strftime("%d %b %Y | %I:%M %p")
    for city in BAR_DATA:
        if city in text:
            return f"🍺 **Best Bars in {city.title()}**\n🕒 {now}\n\n" + "\n".join(
                [f"- {b}" for b in BAR_DATA[city]]
            )
    return None

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=temperature,
    streaming=True
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh;text-align:center;">
    <h1>💬 NeoMind AI</h1>
    <p style="opacity:0.7;">Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content, unsafe_allow_html=True)

# ---------------- CHAT INPUT (DO NOT TOUCH) ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    reply = smart_answer(prompt)

    if reply:
        st.session_state.messages.append(AIMessage(content=reply))
        with st.chat_message("assistant"):
            st.markdown(reply)
    else:
        with st.chat_message("assistant"):
            box = st.empty()
            full = ""
            try:
                for chunk in llm.stream(st.session_state.messages):
                    if chunk.content:
                        full += chunk.content
                        box.markdown(full)
            except:
                full = "⚠️ Too many requests. Please wait and try again."
                box.markdown(full)

        st.session_state.messages.append(AIMessage(content=full))
