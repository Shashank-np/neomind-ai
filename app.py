import streamlit as st
import requests
from datetime import datetime, timedelta
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

# 🔒 Rate-limit lock
if "cooldown_until" not in st.session_state:
    st.session_state.cooldown_until = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
        st.session_state.cooldown_until = None
        st.rerun()

    st.divider()
    st.subheader("🆘 Help & Feedback")

    feedback = st.text_area(
        "Write your message here…",
        placeholder="Type your feedback here..."
    )

    if st.button("Send Feedback"):
        if feedback.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={
                    "name": "NeoMind AI User",
                    "email": "no-reply@neomind.ai",
                    "message": feedback
                },
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")
        else:
            st.warning("Please write something")

    st.caption("Created by **Shashank N P**")

# ---------------- THEME VARIABLES ----------------
bg = "linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c)"
sidebar_bg = "#0b1f2a"
text = "#ffffff"
chat_input_bg = "#000000"
border = "#ffffff"
placeholder = "#bbbbbb"

# ---------------- CHAT INPUT CSS (FLAT STYLE) ----------------
st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg};
}}
[data-testid="stSidebar"] * {{
    color: {text} !important;
}}

/* REMOVE BACK FRAME */
[data-testid="stChatInput"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 12px !important;
}}

/* FLAT INPUT BAR */
[data-testid="stChatInput"] textarea {{
    background-color: {chat_input_bg} !important;
    color: {text} !important;
    border: 1.5px solid {border} !important;
    border-radius: 8px !important;
    padding: 14px 56px 14px 16px !important;
    font-size: 16px !important;
    min-height: 50px !important;
    resize: none !important;
}}

/* PLACEHOLDER */
[data-testid="stChatInput"] textarea::placeholder {{
    color: {placeholder} !important;
}}

/* SEND ARROW (RIGHT SIDE) */
[data-testid="stChatInput"] button {{
    background-color: transparent !important;
    border: none !important;
    width: 36px !important;
    height: 36px !important;
    margin-bottom: 6px !important;
}}

/* MOBILE */
@media (max-width: 768px) {{
    [data-testid="stChatInput"] textarea {{
        font-size: 15px !important;
        padding: 12px 52px 12px 14px !important;
    }}
}}
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
            return f"""
🍺 **Best Bars in {city.title()}**
🕒 {now}

""" + "\n".join([f"- {b}" for b in BAR_DATA[city]])
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

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    now = datetime.now()

    # ⛔ Cooldown active
    if st.session_state.cooldown_until and now < st.session_state.cooldown_until:
        with st.chat_message("assistant"):
            st.warning("⚠️ Please wait a few seconds before sending another message.")
    else:
        st.session_state.messages.append(HumanMessage(content=prompt))

        with st.chat_message("user"):
            st.markdown(prompt)

        reply = smart_answer(prompt)

        if reply:
            st.session_state.messages.append(AIMessage(content=reply))
            with st.chat_message("assistant"):
                st.markdown(reply, unsafe_allow_html=True)
        else:
            if not st.session_state.system_added:
                st.session_state.messages.insert(
                    0,
                    SystemMessage(content="You are NeoMind AI. Be accurate, contextual and helpful.")
                )
                st.session_state.system_added = True

            with st.chat_message("assistant"):
                box = st.empty()
                full = ""
                try:
                    for chunk in llm.stream(st.session_state.messages):
                        if chunk.content:
                            full += chunk.content
                            box.markdown(full, unsafe_allow_html=True)
                except Exception:
                    # ⏱ lock for 8 seconds
                    st.session_state.cooldown_until = now + timedelta(seconds=8)
                    full = "⚠️ Too many requests right now. Please wait a few seconds."
                    box.markdown(full)

            st.session_state.messages.append(AIMessage(content=full))

