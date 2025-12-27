import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------- LOAD ENV ----------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="User GPT",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1f1c2c);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Sidebar glass effect */
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Chat bubbles */
.stChatMessage[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, #6e7ff3, #00e5ff);
    border-radius: 18px;
    padding: 12px;
    color: black;
}

.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 12px;
}

/* Input box */
textarea {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Buttons */
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_added" not in st.session_state:
    st.session_state.system_added = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🤖 User GPT")


    model = st.selectbox(
        "Choose Model",
        ["llama-3.3-70b-versatile"]
    )
    temperature = st.slider("Creativity", 0.0, 1.0, 0.6)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
        st.rerun()

    st.markdown("---")
    st.markdown("**👨‍💻 Project By:** Shashank N P")

# ---------------- INIT LLM ----------------
llm = ChatGroq(
    model=model,
    api_key=api_key,
    temperature=temperature
)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>💬 User GPT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your personal AI assistant</p>", unsafe_allow_html=True)

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Ask anything...")

if prompt:
    if not st.session_state.system_added:
        st.session_state.messages.insert(
            0,
            SystemMessage(
                content="You are a helpful, clear, and concise AI assistant. Explain concepts simply with examples."
            )
        )
        st.session_state.system_added = True

    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = llm.invoke(st.session_state.messages)
        ai_msg = AIMessage(content=response.content)
    except Exception as e:
        ai_msg = AIMessage(content=f"❌ Groq error: {e}")

    st.session_state.messages.append(ai_msg)

    with st.chat_message("assistant"):
        st.markdown(ai_msg.content)
