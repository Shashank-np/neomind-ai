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

    feedback = st.text_area("Write your message here…", placeholder="Type your feedback here...")

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
    bg_gradient = "linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c)"
    sidebar_bg = "#0b1f2a"
    text_color = "#ffffff"
    input_bg = "#1e2a33"
    border_color = "#ffffff"
    button_bg = "#000000"
    button_text = "#ffffff"
else:
    bg_gradient = "linear-gradient(-45deg,#f4f6f8,#eef1f4,#e6ebf0,#f4f6f8)"
    sidebar_bg = "#ffffff"
    text_color = "#000000"
    input_bg = "#ffffff"
    border_color = "#000000"
    button_bg = "#000000"
    button_text = "#ffffff"

# ---------------- GLOBAL CSS FIX ----------------
st.markdown(f"""
<style>

/* App background */
.stApp {{
    background: {bg_gradient};
    background-size: 400% 400%;
    animation: gradientMove 16s ease infinite;
    color: {text_color};
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {sidebar_bg};
}}
[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

/* Buttons */
.stButton > button {{
    background-color: {button_bg} !important;
    color: {button_text} !important;
    border-radius: 8px;
    border: 1px solid {border_color};
    font-weight: 600;
}}
.stButton > button:hover {{
    opacity: 0.9;
}}

/* Text area + inputs */
textarea, input {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 2px solid {border_color} !important;
    border-radius: 8px;
}}

/* Chat bubbles */
.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg,#ff4d4d,#ff7a18);
    color: #000000;
    border-radius: 16px;
    padding: 12px;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: rgba(255,255,255,0.12);
    color: {text_color};
    border-radius: 16px;
    padding: 12px;
}}

/* Animation */
@keyframes gradientMove {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

</style>
""", unsafe_allow_html=True)

# ---------------- SMART LOCAL ANSWER ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    city = "Bengaluru"

    bars = [
        "Toit – Indiranagar",
        "Big Pitcher – Indiranagar",
        "The Biere Club – Lavelle Road",
        "Skyye – Rooftop Lounge",
        "Drunken Daddy – Koramangala"
    ]

    if "bar" in text and ("near me" in text or "suggest" in text):
        return f"### 🍺 Best bars in {city}\n" + "\n".join(f"- {b}" for b in bars)

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
        st.markdown(msg.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
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
                0,
                SystemMessage(content="You are NeoMind AI, fast and helpful.")
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
