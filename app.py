import streamlit as st
import requests
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

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.session_state.system_added = False
            st.rerun()

    with col2:
        toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if toggle != st.session_state.dark_mode:
            st.session_state.dark_mode = toggle
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
if st.session_state.dark_mode:
    bg = "linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c)"
    sidebar_bg = "#0b1f2a"
    text = "#ffffff"
    input_bg = "#000000"
    border = "#ffffff"
    btn_bg = "#000000"
    btn_text = "#ffffff"
    placeholder = "#bbbbbb"
else:
    bg = "linear-gradient(-45deg,#f4f6f8,#eef1f4,#e6ebf0,#f4f6f8)"
    sidebar_bg = "#ffffff"
    text = "#000000"
    input_bg = "#ffffff"
    border = "#000000"
    btn_bg = "#ffffff"
    btn_text = "#000000"
    placeholder = "#555555"

# ---------------- CSS ----------------
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

.stButton > button {{
    background: {btn_bg} !important;
    color: {btn_text} !important;
    border: 2px solid {border} !important;
    border-radius: 10px;
    font-weight: 600;
}}

[data-testid="stChatInput"] textarea {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 10px !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: {placeholder} !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- SMART LOCAL ANSWER ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    if "bar" in text and ("near me" in text or "suggest" in text):
        return """🍺 **Best bars in Bengaluru**

- Toit – Indiranagar  
- Big Pitcher – Indiranagar  
- The Biere Club – Lavelle Road  
- Skyye – Rooftop Lounge  
- Drunken Daddy – Koramangala
"""
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
        st.markdown(f"<div style='color:{text}'>{msg.content}</div>", unsafe_allow_html=True)

# ---------------- CHAT INPUT (FIXED) ----------------
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
            st.markdown(f"<div style='color:{text}'>{reply}</div>", unsafe_allow_html=True)
    else:
        if not st.session_state.system_added:
            st.session_state.messages.insert(
                0,
                SystemMessage(content="You are NeoMind AI, fast and helpful.")
            )
            st.session_state.system_added = True

        with st.chat_message("assistant"):
            placeholder_box = st.empty()
            full = ""
            for chunk in llm.stream(st.session_state.messages):
                if chunk.content:
                    full += chunk.content
                    placeholder_box.markdown(
                        f"<div style='color:{text}'>{full}</div>",
                        unsafe_allow_html=True
                    )

        st.session_state.messages.append(AIMessage(content=full))
