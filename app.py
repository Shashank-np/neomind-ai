import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

from bs4 import BeautifulSoup
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------- THEME COLORS ----------------
if st.session_state.dark_mode:
    BG_MAIN = "#0f172a"
    BG_SIDEBAR = "#020617"
    BG_CARD = "#020617"
    TEXT_COLOR = "#ffffff"
    BORDER = "#334155"
    PLACEHOLDER = "#ffffff"
    SEND_BG = "#1e293b"
else:
    BG_MAIN = "#e6f7ff"
    BG_SIDEBAR = "#d9f0ff"
    BG_CARD = "#ffffff"
    TEXT_COLOR = "#000000"
    BORDER = "#aaccee"
    PLACEHOLDER = "#5b7fa3"
    SEND_BG = "#ffffff"

# ---------------- USER TIMEZONE ----------------
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART LOGIC ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.today().astimezone(tz)

    time_questions = [
        "time", "what is time", "what's time",
        "current time", "what is the time",
        "time?", "time please", "tell time", "show time"
    ]

    if text in time_questions:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "creator full name" in text:
        return "**Shashank N P**"
    if "creator" in text:
        return "**Shashank**"
    if "your name" in text:
        return "**Rossie**"

    if "tomorrow" in text:
        tmr = now + timedelta(days=1)
        return f"📅 **Tomorrow:** {tmr.strftime('%d %B %Y')} ({tmr.strftime('%A')})"

    if "today" in text or text == "date":
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- VIDEO SEARCH ----------------
def video_suggestion(query):
    video_keywords = ["video", "youtube", "watch", "explain", "tutorial", "lecture"]

    if not any(k in query.lower() for k in video_keywords):
        return None

    try:
        yt_url = "https://www.youtube.com/results"
        params = {"search_query": query}
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(yt_url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "/watch?v=" in href:
                link = "https://www.youtube.com" + href
                if link not in links:
                    links.append(link)
            if len(links) == 3:
                break

        if not links:
            return None

        reply = "🎥 **Recommended Informative Videos**\n\n"
        for i, link in enumerate(links, 1):
            reply += f"{i}. {link}\n"

        return reply

    except:
        return None

# ---------------- SMART WEB SCRAPING ----------------
def web_scrape_structured(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        google_url = "https://www.google.com/search"
        params = {"q": query}

        res = requests.get(google_url, headers=headers, params=params, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        source_link = None
        for a in soup.select("a"):
            href = a.get("href", "")
            if href.startswith("/url?q="):
                source_link = href.split("/url?q=")[1].split("&")[0]
                break

        if not source_link:
            return None

        page = requests.get(source_link, headers=headers, timeout=5)
        psoup = BeautifulSoup(page.text, "html.parser")

        title = psoup.title.string.strip() if psoup.title else query.title()

        paragraphs = psoup.find_all("p")
        points = []

        for p in paragraphs:
            text = p.get_text().strip()
            if 50 < len(text) < 200:
                points.append(text)
            if len(points) == 6:
                break

        if not points:
            return None

        response = f"### **{title}**\n\n"
        response += "**Overview**\n\n"

        for p in points:
            response += f"- {p}\n"

        response += f"\n🌐 **Source:** {source_link}"

        return response

    except:
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
            st.rerun()
    with col2:
        st.toggle("🌙 Dark Mode", key="dark_mode")

    st.divider()
    st.subheader("🆘 Help & Feedback")

    feedback = st.text_area("Share your feedback or suggestions")
    if st.button("Send Feedback"):
        if feedback.strip():
            requests.post(
                "https://formspree.io/f/xblanbjk",
                data={"message": feedback},
                headers={"Accept": "application/json"}
            )
            st.success("✅ Feedback sent!")

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature,
)

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh;text-align:center;">
<h1>💬 NeoMind AI</h1>
<p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages:
    with st.chat_message("user" if isinstance(m, HumanMessage) else "assistant"):
        st.markdown(m.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT HANDLER ----------------
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = (
            smart_answer(prompt)
            or video_suggestion(prompt)
            or web_scrape_structured(prompt)
            or llm.invoke(st.session_state.messages).content
        )

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
