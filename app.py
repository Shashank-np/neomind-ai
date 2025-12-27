import streamlit as st
import requests
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

# ---------------- LIGHT BLUE UI (OLD STYLE) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #e6f4ff, #cfe9ff);
    color: #003366;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #d9f0ff, #bfe3ff);
}

.stChatMessage[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, #6ec6ff, #4dabf7);
    border-radius: 16px;
    padding: 12px;
    color: black;
}

.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 12px;
    color: #003366;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_added" not in st.session_state:
    st.session_state.system_added = False

# ---------------- SIMPLE LOCAL ANSWERS ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    city = "Bengaluru"

    data = {
        "bar": ["Toit", "Big Pitcher", "Skyye", "Drunken Daddy"],
        "restaurant": ["Meghana Foods", "Truffles", "Empire", "MTR"],
        "cafe": ["Third Wave Coffee", "Blue Tokai", "Glen's Bakehouse"],
        "places": ["Lalbagh", "Cubbon Park", "ISKCON", "Nandi Hills"]
    }

    for key, items in data.items():
        if key in text:
            return f"Here are popular {key}s in {city}:\n\n" + "\n".join(f"- {i}" for i in items)

    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

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
                }
            )
            st.success("✅ Feedback sent!")

    st.caption("Created by **Shashank N P**")

# ---------------- FREE & STABLE MODEL ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # ✅ FREE + UNLIMITED
    api_key=api_key,
    temperature=temperature,
    streaming=False
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh; text-align:center;">
    <h1>💬 NeoMind AI</h1>
    <p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT LOGIC ----------------
if prompt:
    if not st.session_state.system_added:
        st.session_state.messages.insert(
            0,
            SystemMessage(content="You are a friendly, simple, and clear AI assistant.")
        )
        st.session_state.system_added = True

    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    local = smart_answer(prompt)

    with st.chat_message("assistant"):
        if local:
            answer = local
        else:
            try:
                response = llm.invoke(st.session_state.messages)
                answer = response.content
            except Exception:
                answer = "I’m here and ready. Please ask again."

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
