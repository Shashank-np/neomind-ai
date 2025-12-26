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

    feedback_side = st.text_area(
        "Write your message here…",
        placeholder="Type your feedback here..."
    )

    if st.button("Send Feedback"):
        if feedback_side.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={
                    "name": "NeoMind AI User",
                    "email": "no-reply@neomind.ai",
                    "message": feedback_side
                },
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")
        else:
            st.warning("Please write something")

    st.caption("Created by **Shashank N P**")

# ---------------- THEME ----------------
if st.session_state.dark_mode:
    bg = "linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c)"
    sidebar_bg = "#0b1f2a"
    text = "#ffffff"
    input_bg = "#0f2027"
    border = "#ffffff"
    placeholder = "#bfc7ce"
    user_bg = "#2e3f4a"
    ai_bg = "linear-gradient(135deg,#203a43,#2c5364)"
else:
    bg = "linear-gradient(-45deg,#f4f6f8,#eef1f4,#e6ebf0,#f4f6f8)"
    sidebar_bg = "#ffffff"
    text = "#000000"
    input_bg = "#f4f6f8"
    border = "#000000"
    placeholder = "#555555"
    user_bg = "#dfe5ea"
    ai_bg = "#ffffff"

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
    background: transparent !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 10px;
    font-weight: 600;
}}

[data-testid="stChatInput"] textarea {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 12px !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {placeholder} !important;
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: {user_bg};
    color: {text};
    border-radius: 14px;
    padding: 12px;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: {ai_bg};
    color: {text};
    border-radius: 14px;
    padding: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE / HERO (FIXED) ----------------
st.markdown(
    f"""
    <div style="text-align:center; margin-top:20px; margin-bottom:30px;">
        <h1 style="margin-bottom:5px;">💬 NeoMind AI</h1>
        <p style="opacity:0.75;">Ask. Think. Generate.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---------------- MAIN FEEDBACK BOX ----------------
st.markdown("### 📝 Feedback")
feedback_main = st.text_area(
    "",
    placeholder="Share your feedback about NeoMind AI…",
    key="main_feedback"
)

if st.button("📩 Submit Feedback"):
    if feedback_main.strip():
        requests.post(
            "https://formspree.io/f/xblanbjk",
            data={
                "name": "NeoMind AI User",
                "email": "no-reply@neomind.ai",
                "message": feedback_main
            },
            headers={"Accept": "application/json"}
        )
        st.success("✅ Thanks for your feedback!")
        st.session_state.main_feedback = ""
    else:
        st.warning("Please write feedback before submitting")

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder_box = st.empty()
        full = ""

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=temperature,
            streaming=True
        )

        for chunk in llm.stream(st.session_state.messages):
            if chunk.content:
                full += chunk.content
                placeholder_box.markdown(full)

    st.session_state.messages.append(AIMessage(content=full))
