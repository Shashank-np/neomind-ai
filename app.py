import streamlit as st
import requests
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from groq import RateLimitError

# ---------------- API KEY (STREAMLIT SAFE) ----------------
api_key = st.secrets["GROQ_API_KEY"]

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- UI / CSS (FROM OLD CODE – UNCHANGED) ----------------
st.markdown("""
<style>
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
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(12px);
}
.stChatMessage[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, #ff4d4d, #ff7a18);
    border-radius: 16px;
    padding: 12px;
    color: black;
}
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_added" not in st.session_state:
    st.session_state.system_added = False

# ---------------- SIDEBAR (OLD UI, SAFE LOGIC) ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    model = st.selectbox(
        "Choose Model",
        ["llama-3.3-70b-versatile"]
    )

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
                },
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")
        else:
            st.warning("Please write something")

    st.caption("Created by **Shashank N P**")

# ---------------- LLM (SAFE – NO STREAMING) ----------------
llm = ChatGroq(
    model=model,
    api_key=api_key,
    temperature=temperature,
    streaming=False
)

# ---------------- HERO TITLE (OLD UI) ----------------
st.markdown("""
<div style="margin-top:30vh; text-align:center;">
    <h1>💬 NeoMind AI</h1>
    <p style="opacity:0.8;">Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT LOGIC (FROM USER GPT – STABLE) ----------------
if prompt:
    if not st.session_state.system_added:
        st.session_state.messages.insert(
            0,
            SystemMessage(
                content="You are a helpful, clear, and concise AI assistant. Explain concepts simply with examples."
            )
        )
        st.session_state.system_added = True

    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        try:
            response = llm.invoke(st.session_state.messages)
            answer = response.content

        except RateLimitError:
            answer = (
                "⏳ I'm temporarily busy due to high usage.\n\n"
                "Please wait a few minutes and try again."
            )

        except Exception:
            answer = (
                "⚠️ Something went wrong.\n\n"
                "Please try again."
            )

        # ChatGPT-like typing (safe)
        shown = ""
        for ch in answer:
            shown += ch
            placeholder.markdown(shown)

        st.session_state.messages.append(AIMessage(content=answer))
