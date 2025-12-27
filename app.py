import streamlit as st
import requests
from datetime import datetime
import time
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

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
        st.session_state.is_generating = False
        st.rerun()

# ---------------- CITY DATA ----------------
BAR_DATA = {
    "bengaluru": [
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
            return (
                f"🍺 **Best Bars in {city.title()}**\n"
                f"🕒 {now}\n\n" +
                "\n".join([f"- {b}" for b in BAR_DATA[city]])
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

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER (FINAL & CORRECT) ----------------
if prompt and not st.session_state.is_generating:

    clean_prompt = prompt.strip()

    # 🚫 IGNORE NON-MEANINGFUL INPUT
    if len(clean_prompt.split()) < 3:
        pass  # do nothing, just wait for real input

    else:
        st.session_state.is_generating = True
        st.session_state.messages.append(HumanMessage(content=clean_prompt))

        with st.chat_message("user"):
            st.markdown(clean_prompt)

        reply = smart_answer(clean_prompt)

        if reply:
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append(AIMessage(content=reply))
            st.session_state.is_generating = False

        else:
            if not st.session_state.system_added:
                st.session_state.messages.insert(
                    0,
                    SystemMessage(
                        content="You are NeoMind AI. Be accurate, contextual and helpful."
                    )
                )
                st.session_state.system_added = True

            with st.chat_message("assistant"):
                box = st.empty()
                full = ""

                try:
                    for chunk in llm.stream(st.session_state.messages):
                        if chunk.content:
                            full += chunk.content
                            box.markdown(full)
                except Exception:
                    time.sleep(2)
                    for chunk in llm.stream(st.session_state.messages):
                        if chunk.content:
                            full += chunk.content
                            box.markdown(full)

            st.session_state.messages.append(AIMessage(content=full))
            st.session_state.is_generating = False
