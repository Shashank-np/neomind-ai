import streamlit as st
import requests
import re
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

# ---------------- SKY BLUE ANIMATED UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #dff3ff, #b6e6ff);
    background-size: 200% 200%;
    animation: bgMove 12s ease infinite;
    color: #003366;
}

@keyframes bgMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #cfeeff, #a9dcff);
}

.stChatMessage[data-testid="stChatMessage-user"] {
    background: #4dabf7;
    color: black;
    border-radius: 16px;
    padding: 12px;
}

.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: #ffffff;
    color: #003366;
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

# ---------------- CITY-AWARE SMART ANSWER ----------------
def extract_city(text):
    cities = ["bengaluru", "bangalore", "davanagere", "mysuru", "mangalore", "hubli"]
    for city in cities:
        if city in text:
            return city.title()
    return None

def smart_answer(prompt: str):
    text = prompt.lower()
    city = extract_city(text)

    places = {
        "Davanagere": {
            "bar": ["Lion’s Bar", "Mehfil Bar", "Relax Bar"],
            "places": ["Kunduvada Kere", "Anjaneya Temple", "Glass House"]
        },
        "Bengaluru": {
            "bar": ["Toit", "Big Pitcher", "Skyye", "Drunken Daddy"],
            "places": ["Lalbagh", "Cubbon Park", "ISKCON", "Bangalore Palace"]
        }
    }

    for category in ["bar", "places"]:
        if category in text:
            if not city:
                return "📍 Please tell me the city so I can give accurate suggestions."
            if city in places and category in places[city]:
                return f"Here are popular {category}s in **{city}**:\n\n" + \
                       "\n".join(f"- {p}" for p in places[city][category])

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

# ---------------- FREE CHAT MODEL ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # ✅ free & stable
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

# ---------------- CHAT HANDLER ----------------
if prompt:
    if not st.session_state.system_added:
        st.session_state.messages.insert(
            0,
            SystemMessage(content="You are a helpful assistant like ChatGPT.")
        )
        st.session_state.system_added = True

    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        local = smart_answer(prompt)

        if local:
            answer = local
        else:
            response = llm.invoke(st.session_state.messages)
            answer = response.content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
