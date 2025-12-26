import streamlit as st
import requests
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

api_key = st.secrets["GROQ_API_KEY"]

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_added" not in st.session_state:
    st.session_state.system_added = False

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# --------------------------------------------------
# THEME VARIABLES
# --------------------------------------------------
if st.session_state.dark_mode:
    BG = "#0b1f2a"
    SIDEBAR = "#071922"
    TEXT = "#ffffff"
    INPUT_BG = "#1e2a33"
    BORDER = "#ffffff"
    BTN_BG = "#000000"
else:
    BG = "#f2f4f7"
    SIDEBAR = "#ffffff"
    TEXT = "#000000"
    INPUT_BG = "#ffffff"
    BORDER = "#000000"
    BTN_BG = "#000000"

# --------------------------------------------------
# GLOBAL CSS (FIXES EVERYTHING)
# --------------------------------------------------
st.markdown(f"""
<style>

/* APP */
.stApp {{
    background: {BG};
    color: {TEXT};
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {SIDEBAR};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

/* BUTTONS */
.stButton > button {{
    background: {BTN_BG};
    color: #ffffff !important;
    border-radius: 8px;
    border: 1px solid {BORDER};
    font-weight: 600;
}}

/* TEXTAREA + INPUT */
textarea, input {{
    background: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 2px solid {BORDER} !important;
    border-radius: 8px;
}}

/* CHAT INPUT — REMOVE DOUBLE FRAME */
div[data-testid="stChatInput"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-testid="stChatInput"] textarea {{
    background: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 2px solid {BORDER} !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
}}

/* CHAT BUBBLES */
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg,#ff4d4d,#ff7a18);
    color: #000000;
    border-radius: 16px;
    padding: 12px;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: rgba(255,255,255,0.12);
    color: {TEXT};
    border-radius: 16px;
    padding: 12px;
}}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
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

# --------------------------------------------------
# SMART LOCAL ANSWER
# --------------------------------------------------
def smart_answer(prompt: str):
    if "bar" in prompt.lower():
        return """### 🍺 Best bars in Bengaluru
- Toit – Indiranagar
- Big Pitcher – Indiranagar
- Skyye – Rooftop Lounge
- Drunken Daddy – Koramangala"""
    return None

# --------------------------------------------------
# LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=temperature,
    streaming=True
)

# --------------------------------------------------
# HERO
# --------------------------------------------------
if not st.session_state.messages:
    st.markdown("""
    <div style="margin-top:30vh;text-align:center;">
        <h1>💬 NeoMind AI</h1>
        <p style="opacity:0.7;">Ask. Think. Generate.</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# --------------------------------------------------
# INPUT
# --------------------------------------------------
prompt = st.chat_input("Ask NeoMind AI anything...")

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    local = smart_answer(prompt)
    if local:
        with st.chat_message("assistant"):
            st.markdown(local)
        st.session_state.messages.append(AIMessage(content=local))
    else:
        if not st.session_state.system_added:
            st.session_state.messages.insert(
                0, SystemMessage(content="You are NeoMind AI, fast and helpful.")
            )
            st.session_state.system_added = True

        with st.chat_message("assistant"):
            placeholder = st.empty()
            response = ""
            for chunk in llm.stream(st.session_state.messages):
                if chunk.content:
                    response += chunk.content
                    placeholder.markdown(response)

        st.session_state.messages.append(AIMessage(content=response))
