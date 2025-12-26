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

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
        st.rerun()

    st.caption("Created by **Shashank N P**")

# ---------------- CITY DATA ----------------
BAR_DATA = {
    "bengaluru": [
        "Toit – Indiranagar",
        "Big Pitcher – Indiranagar",
        "The Biere Club – Lavelle Road",
        "Skyye – UB City",
        "Drunken Daddy – Koramangala"
    ],
    "bangalore": [
        "Toit – Indiranagar",
        "Big Pitcher – Indiranagar",
        "The Biere Club – Lavelle Road",
        "Skyye – UB City",
        "Drunken Daddy – Koramangala"
    ],
    "chitradurga": [
        "Hotel Mayura Bar – Chitradurga",
        "SLV Bar & Restaurant – Chitradurga",
        "Naveen Bar – Chitradurga",
        "Local Permit Room – Chitradurga"
    ],
    "mysuru": [
        "The Road – Radisson Blu",
        "Purple Haze – Mysuru",
        "Pelican Pub – Mysuru"
    ]
}

# ---------------- GET USER CITY (IP) ----------------
def get_ip_city():
    try:
        res = requests.get("https://ipinfo.io/json").json()
        return res.get("city", "").lower()
    except:
        return ""

# ---------------- SMART ANSWER ----------------
def smart_answer(prompt):
    text = prompt.lower()

    if "bar" not in text:
        return None

    # 1️⃣ Check explicit city in prompt
    for city in BAR_DATA:
        if city in text:
            bars = BAR_DATA[city]
            return f"""
🍺 **Best Bars in {city.title()}**

""" + "\n".join([f"- {b}" for b in bars])

    # 2️⃣ Handle "near me"
    if "near me" in text:
        city = get_ip_city()
        if city in BAR_DATA:
            bars = BAR_DATA[city]
            return f"""
📍 **Bars Near You ({city.title()})**

""" + "\n".join([f"- {b}" for b in bars])
        else:
            return "❌ Sorry, I couldn't find bar data for your location."

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
    <p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---------------- CHAT INPUT ----------------
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
            st.markdown(reply)
    else:
        if not st.session_state.system_added:
            st.session_state.messages.insert(
                0, SystemMessage(content="You are NeoMind AI. Be accurate.")
            )
            st.session_state.system_added = True

        with st.chat_message("assistant"):
            box = st.empty()
            full = ""
            for chunk in llm.stream(st.session_state.messages):
                if chunk.content:
                    full += chunk.content
                    box.markdown(full)

        st.session_state.messages.append(AIMessage(content=full))
