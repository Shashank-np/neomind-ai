import streamlit as st
import requests
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from groq import RateLimitError

# ---------------- API KEY (FROM SECOND CODE) ----------------
api_key = st.secrets["GROQ_API_KEY"]

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- CSS (UNCHANGED – FROM SECOND CODE) ----------------
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

# ---------------- SMART ANSWER (FROM FIRST CODE) ----------------
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
        if key in text and ("best" in text or "near me" in text or "suggest" in text):
            formatted = "\n".join(f"- {i}" for i in items)
            return f"""
Here are some popular **{key}s in {city}**:

{formatted}
"""
    return None

# ---------------- SIDEBAR (SECOND CODE) ----------------
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
                },
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")
        else:
            st.warning("Please write something")

    st.caption("Created by **Shashank N P**")

# ---------------- LLM (SAFE – FROM SECOND CODE) ----------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=temperature,
    streaming=False   # 🔒 critical
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

# ---------------- CHAT HANDLER (FIRST CODE BEHAVIOR, SECOND CODE SAFETY) ----------------
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

            # Simulated streaming (safe)
            displayed = ""
            for ch in answer:
                displayed += ch
                placeholder.markdown(displayed)

            st.session_state.messages.append(AIMessage(content=answer))
