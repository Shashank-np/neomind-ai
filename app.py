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

# ---------------- TIMEZONE ----------------
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

# ---------------- WEB SCRAPE ----------------
def web_scrape_summary(query):
    try:
        res = requests.get(
            f"https://www.google.com/search?q={query}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
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
    st.subheader("🆘 Feedback")
    fb = st.text_area("Share your feedback", placeholder="Tell us what to improve...")
    if st.button("Send Feedback"):
        if fb.strip():
            requests.post("https://formspree.io/f/xblanbjk", data={"message": fb})
            st.success("✅ Feedback sent")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- ANIMATED BACKGROUND ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# ---------------- CHAT UI ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---------------- FIXED MIC SCRIPT ----------------
st.markdown("""
<script>
let recognition;
let listening = false;

function startMic() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition not supported. Use Chrome or Edge.");
    return;
  }

  if (listening && recognition) {
    recognition.stop();
    listening = false;
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onstart = () => {
    listening = true;
  };

  recognition.onresult = (event) => {
    let text = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      text += event.results[i][0].transcript + " ";
    }
    const textarea = window.parent.document.querySelector("textarea");
    if (textarea) {
      textarea.value = text.trim();
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
    }
  };

  recognition.onerror = (e) => {
    console.error("Mic error:", e);
    recognition.stop();
    listening = false;
  };

  recognition.onend = () => {
    listening = false;
  };

  recognition.start();
}
</script>
""", unsafe_allow_html=True)

# ---------------- MIC ICON (LEFT OF SEND ARROW) ----------------
st.markdown("""
<style>
#mic-btn {
  position: fixed;
  bottom: 32px;
  right: 70px;
  font-size: 20px;
  cursor: pointer;
  z-index: 999;
}
</style>
<div id="mic-btn" onclick="startMic()">🎤</div>
""", unsafe_allow_html=True)

# ---------------- ORIGINAL CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything...")

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
