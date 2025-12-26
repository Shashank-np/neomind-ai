import streamlit as st
import requests
from datetime import datetime
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
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.system_added = False
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
    st.write("-------------------------------")
    st.caption("Created by **Shashank N P**")

# ---------------- THEME VARIABLES ----------------
bg = "linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c)"
sidebar_bg = "#0b1f2a"
text = "#ffffff"
chat_input_bg = "#000000"
feedback_bg = "#0f2027"
border = "#ffffff"
btn_bg = "#000000"
btn_text = "#ffffff"
placeholder = "#bbbbbb"

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
    background-color: {chat_input_bg} !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 10px !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: {placeholder} !important;
}}

textarea {{
    background-color: {feedback_bg} !important;
    color: {text} !important;
    border: 2px solid {border} !important;
    border-radius: 10px !important;
}}

textarea::placeholder {{
    color: {placeholder} !important;
}}
</style>
""", unsafe_allow_html=True)

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

# ---------------- IP LOCATION ----------------
def get_ip_city():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5).json()
        return res.get("city", "").lower()
    except:
        return ""

# ---------------- SMART ANSWER ----------------
def smart_answer(prompt: str):
    text = prompt.lower()
    if "bar" not in text:
        return None

    now = datetime.now().strftime("%d %b %Y | %I:%M %p")

    for city in BAR_DATA:
        if city in text:
            return f"""
🍺 **Best Bars in {city.title()}**
🕒 {now}

""" + "\n".join([f"- {b}" for b in BAR_DATA[city]])

    if "near me" in text:
        city = get_ip_city()
        if city in BAR_DATA:
            return f"""
📍 **Bars Near You ({city.title()})**
🕒 {now}

""" + "\n".join([f"- {b}" for b in BAR_DATA[city]])
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
    <p style="opacity:0.7;">Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content, unsafe_allow_html=True)

# ---------------- AUTO SCROLL (NEW) ----------------
def scroll_to_bottom():
    st.markdown(
        """
        <script>
        var element = document.getElementById("bottom-anchor");
        if (element) {
            element.scrollIntoView({behavior: "smooth"});
        }
        </script>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div id="bottom-anchor"></div>', unsafe_allow_html=True)
scroll_to_bottom()

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
            st.markdown(reply, unsafe_allow_html=True)
    else:
        if not st.session_state.system_added:
            st.session_state.messages.insert(
                0,
                SystemMessage(content="You are NeoMind AI. Be accurate, contextual and helpful.")
            )
            st.session_state.system_added = True

        with st.chat_message("assistant"):
            placeholder_box = st.empty()
            full = ""
            for chunk in llm.stream(st.session_state.messages):
                if chunk.content:
                    full += chunk.content
                    placeholder_box.markdown(full, unsafe_allow_html=True)

        st.session_state.messages.append(AIMessage(content=full))

