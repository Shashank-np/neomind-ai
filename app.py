import streamlit as st
import requests
from datetime import datetime
import pytz
import wikipedia
from bs4 import BeautifulSoup
import io

import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

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

# ---------------- USER TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SPEECH TO TEXT ----------------
def speech_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(io.BytesIO(audio_bytes))

    with audio_file as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio)
    except:
        return ""

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
    except wikipedia.DisambiguationError:
        return "⚠️ Multiple results found. Please be specific."
    except wikipedia.PageError:
        return "❌ No page found."
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

    feedback = st.text_area(
        "Share your feedback or suggestions",
        placeholder="Tell us what to improve..."
    )

    if st.button("Send Feedback"):
        if feedback.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"message": feedback},
                    headers={"Accept": "application/json"},
                    timeout=5
                )
                st.success("✅ Feedback sent. Thank you!")
            except:
                st.error("❌ Failed to send feedback.")
        else:
            st.warning("⚠️ Please write feedback first.")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------- INPUT + MIC ----------------
col1, col2 = st.columns([0.9, 0.1])

with col1:
    prompt = st.chat_input("Ask NeoMind AI anything…")

with col2:
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        key="mic"
    )

if audio and "bytes" in audio:
    voice_text = speech_to_text(audio["bytes"])
    if voice_text:
        prompt = voice_text
        st.toast(f"🎙️ You said: {voice_text}")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = smart_answer(prompt)

        if not answer:
            answer = image_info_response(prompt)

        if not answer:
            answer = web_scrape_summary(prompt)

        if not answer:
            try:
                answer = llm.invoke(st.session_state.messages).content
            except Exception:
                answer = (
                    "⚠️ **Maximum chat limit reached.**\n\n"
                    "👉 Please click **Clear Chat** and try again."
                )

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
