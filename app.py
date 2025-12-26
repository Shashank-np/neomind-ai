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

# ---------------- GOOGLE SEARCH CONSOLE VERIFICATION ----------------
st.markdown("""
<meta name="google-site-verification" content="abc123XYZ456" />
""", unsafe_allow_html=True)

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

# ---------------- THEME (FAST SWITCH) ----------------
if st.session_state.dark_mode:
    bg_gradient = """
        linear-gradient(-45deg,
        #0f2027,
        #203a43,
        #2c5364,
        #1f1c2c)
    """
    sidebar_bg = "rgba(0,0,0,0.45)"
    text_color = "white"
    assistant_bg = "rgba(255,255,255,0.08)"
else:
    bg_gradient = """
        linear-gradient(-45deg,
        #fdfbfb,
        #ebedee,
        #dfe9f3,
        #f6f7f8)
    """
    sidebar_bg = "rgba(255,255,255,0.9)"
    text_color = "#111"
    assistant_bg = "rgba(0,0,0,0.06)"

st.markdown(f"""
<style>
.stApp {{
    background: {bg_gradient};
    background-size: 400% 400%;
    animation: gradientMove 18s ease infinite;
    color: {text_color};
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg};
    backdrop-filter: blur(14px);
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg, #ff4d4d, #ff7a18);
    border-radius: 16px;
    padding: 12px;
    color: black;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: {assistant_bg};
    border-radius: 16px;
    padding: 12px;
}}

@keyframes gradientMove {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
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
<div style="margin-top:30vh; text-align:center;">
    <h1>💬 NeoMind AI</h1>
    <p style="opacity:0.8;">Ask. Think. Generate.</p>
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
