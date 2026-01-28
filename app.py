import streamlit as st
import requests
from datetime import datetime
import pytz
import wikipedia

# LangChain + Groq
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
        res = requests.get("https://ipapi.co/json/", timeout=5).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART LOGIC ----------------
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- IMAGE INTENT ----------------
def is_image_request(query):
    keywords = ["image", "photo", "picture", "wallpaper", "pics"]
    return any(k in query.lower() for k in keywords)

# ---------------- IMAGE RESPONSE ----------------
def image_info_response(query):
    if not is_image_request(query):
        return None

    try:
        wikipedia.set_lang("en")
        search_term = query.replace("image", "").strip()
        page = wikipedia.page(search_term, auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)

        title = page.title

        return f"""
### **{title}**

{summary}

📸 **More images**

🔗 https://commons.wikimedia.org/wiki/{title.replace(" ", "_")}  
🔗 https://www.pinterest.com/search/pins/?q={title.replace(" ", "%20")}  

Tell me if you want **HD wallpapers** or **history** 🙌
"""
    except wikipedia.DisambiguationError:
        return "⚠️ I found multiple results. Please be more specific."
    except wikipedia.PageError:
        return "❌ I couldn’t find an exact page for this."
    except Exception:
        return None

# ---------------- MOVIE INFO ----------------
def get_movie_info(title):
    try:
        page = wikipedia.page(title, auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)

        return f"""
### 🎬 **{page.title}**

{summary}

🔗 https://en.wikipedia.org/wiki/{page.title.replace(" ", "_")}
"""
    except:
        return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🧠 NeoMind AI")
    st.caption("Text-based AI Assistant")

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Created by **Shashank N P**")

# ---------------- LLM INIT ----------------
try:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=temperature,
    )
except KeyError:
    st.error("❌ GROQ_API_KEY not found in Streamlit secrets")
    st.stop()

# ---------------- HERO ----------------
st.markdown("""
<div style="margin-top:30vh;text-align:center;">
<h1>💬 NeoMind AI</h1>
<p>Ask. Think. Generate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for m in st.session_state.messages:
    role = "user" if isinstance(m, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(m.content)

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

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
            answer = get_movie_info(prompt)

        if not answer:
            answer = llm.invoke(st.session_state.messages).content

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))
