import streamlit as st
import requests
from datetime import datetime
import pytz
import wikipedia
from bs4 import BeautifulSoup

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ---------------- USER TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART ANSWERS ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- WEB SCRAPING ----------------
def web_scrape_summary(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        snippet = soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
        if snippet:
            return f"🌐 **From the web:**\n\n{snippet.text}"
    except:
        pass
    return None

# ---------------- IMAGE + WIKI ----------------
def image_info_response(query):
    if "image" not in query.lower():
        return None
    try:
        topic = query.replace("image", "").strip()
        wikipedia.set_lang("en")
        page = wikipedia.page(topic, auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)
        return f"""
### 🖼️ **{page.title}**
{summary}
🔗 https://commons.wikimedia.org/wiki/{page.title.replace(" ", "_")}
"""
    except:
        return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- CHAT UI ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------- VOICE SCRIPT ----------------
st.markdown("""
<script>
let recognition;
let listening = false;

function startMic() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech Recognition not supported in this browser");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        listening = true;
        document.getElementById("micStatus").innerText = "🎤 Listening...";
    };

    recognition.onresult = (event) => {
        let text = "";
        for (let i = 0; i < event.results.length; i++) {
            text += event.results[i][0].transcript + " ";
        }
        const textarea = document.getElementById("neoInput");
        textarea.value = text.trim();
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
    };

    recognition.onend = () => {
        listening = false;
        document.getElementById("micStatus").innerText = "";
    };

    recognition.start();
}
</script>
""", unsafe_allow_html=True)

# ---------------- INPUT BAR (UI SAME) ----------------
st.markdown("""
<style>
.chat-bar {
    display: flex;
    gap: 6px;
    align-items: center;
}
.chat-bar textarea {
    width: 100%;
    height: 42px;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #444;
    background-color: #1e1e1e;
    color: white;
}
.chat-btn {
    height: 42px;
    width: 42px;
    border-radius: 50%;
    border: none;
    font-size: 18px;
    cursor: pointer;
}
</style>

<div class="chat-bar">
    <textarea id="neoInput" placeholder="Ask NeoMind AI anything..."></textarea>
    <button class="chat-btn" onclick="startMic()">🎤</button>
    <button class="chat-btn" onclick="sendText()">⬆️</button>
</div>
<div id="micStatus" style="margin-top:6px; font-size:14px;"></div>

<script>
function sendText() {
    const text = document.getElementById("neoInput").value;
    const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (streamlitInput) {
        streamlitInput.value = text;
        streamlitInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
}
</script>
""", unsafe_allow_html=True)

# ---------------- HIDDEN INPUT ----------------
prompt = st.text_input("", key="hidden_input", label_visibility="collapsed")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = smart_answer(prompt) or image_info_response(prompt) or web_scrape_summary(prompt)

        if not answer:
            answer = llm.invoke(st.session_state.messages).content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
