import streamlit as st
import os
import requests
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------- API KEY (STREAMLIT CLOUD) ----------------
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

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ---------------- CSS (UNCHANGED UI + THEME SUPPORT) ----------------
st.markdown(f"""
<style>
:root {{
    --bg-gradient: {"linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1f1c2c)" if st.session_state.theme == "dark"
    else "linear-gradient(-45deg, #f7f7f7, #eaeaea, #dcdcdc, #f7f7f7)"};
    --text-color: {"white" if st.session_state.theme == "dark" else "#111"};
}}

.stApp {{
    background: var(--bg-gradient);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: var(--text-color);
}}

@keyframes gradientBG {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

[data-testid="stSidebar"] {{
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(12px);
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: linear-gradient(135deg, #ff4d4d, #ff7a18);
    border-radius: 16px;
    padding: 12px;
    color: black;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- SMART CHATGPT-LIKE LOGIC ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    city = "Bengaluru"

    knowledge = {
        "bar": [
            "Toit – Indiranagar",
            "Big Pitcher – Indiranagar",
            "The Biere Club – Lavelle Road",
            "Skyye – Rooftop Lounge",
            "Drunken Daddy – Koramangala"
        ],
        "restaurant": [
            "Meghana Foods",
            "Truffles",
            "Empire Restaurant",
            "Absolute Barbeque",
            "MTR"
        ],
        "cafe": [
            "Third Wave Coffee",
            "Glen's Bakehouse",
            "The Hole in the Wall Cafe",
            "Cafe Noir",
            "Blue Tokai Coffee"
        ],
        "places": [
            "Lalbagh Botanical Garden",
            "Cubbon Park",
            "Bangalore Palace",
            "ISKCON Temple",
            "Nandi Hills"
        ]
    }

    for key, items in knowledge.items():
        if key in text and ("near me" in text or "suggest" in text or "best" in text):
            formatted = "\n".join(f"- {i}" for i in items)
            return f"""
Here are some popular **{key}s in {city}** you might like:

{formatted}

👉 Want suggestions for a **different city**? Just tell me the city name.
"""
    return None

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
        theme_toggle = st.toggle(
            "🌙 Dark / ☀️ Light",
            value=(st.session_state.theme == "dark")
        )
        st.session_state.theme = "dark" if theme_toggle else "light"

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
            st.success("✅ Feedback sent to your email!")
        else:
            st.warning("Please write something")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=temperature,
    streaming=True
)

# ---------------- HERO TITLE ----------------
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

# ---------------- HANDLE CHAT ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    local_reply = smart_answer(prompt)

    if local_reply:
        with st.chat_message("assistant"):
            st.markdown(local_reply)
        st.session_state.messages.append(AIMessage(content=local_reply))
    else:
        if not st.session_state.system_added:
            st.session_state.messages.insert(
                0,
                SystemMessage(
                    content="You are NeoMind AI, a friendly, fast, and clear assistant."
                )
            )
            st.session_state.system_added = True

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in llm.stream(st.session_state.messages):
                if chunk.content:
                    full_response += chunk.content
                    placeholder.markdown(full_response)

        st.session_state.messages.append(AIMessage(content=full_response))
