import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
import wikipedia
from bs4 import BeautifulSoup

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

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ **Current time:** {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 **Today:** {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- IMAGE INTENT DETECTOR ----------------
def is_image_request(query):
    keywords = ["image", "photo", "pictures", "wallpaper", "pics"]
    return any(k in query.lower() for k in keywords)

# ---------------- STRUCTURED IMAGE RESPONSE ----------------
def image_info_response(query):
    if not is_image_request(query):
        return None

    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(query.replace("image", "").strip(), auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)

        title = page.title

        response = f"""
### **{title}**

Here are some images of **{title}** — sourced from trusted public image galleries and references.

{summary}

📌 **Quick Info (so you know what the images represent)**

- **{title}** is a well-known historical and cultural landmark.
- The images show important architectural views and surroundings.
- These visuals are commonly used for educational and devotional purposes.

📸 **More photos & wallpapers**

If you want different angles or high-resolution wallpapers, explore these trusted galleries:

🔗 **Wikipedia Media:** https://commons.wikimedia.org/wiki/{title.replace(" ", "_")}  
🔗 **Pinterest HD Images:** https://www.pinterest.com/search/pins/?q={title.replace(" ", "%20")}  
🔗 **Getty Images:** https://www.gettyimages.com/photos/{title.replace(" ", "-")}  
🔗 **Adobe Stock:** https://stock.adobe.com/search?k={title.replace(" ", "+")}

Let me know if you want **download links**, **history**, or **visiting information** 🙏✨
"""
        return response

    except:
        return None

# ---------------- MOVIE SEARCH ----------------
def get_movie_info(title):
    try:
        page = wikipedia.page(title, auto_suggest=True)
        summary = wikipedia.summary(page.title, sentences=2)

        title = page.title

        response = f"""
### **{title}**

🎥 **Movie Info**

{summary}

📺 **Trailer & Reviews**

If you want to watch the trailer or read reviews, explore these trusted links:

🔗 **IMDB:** https://www.imdb.com/title/{page.pageid}/  
🔗 **Rotten Tomatoes:** https://www.rottentomatoes.com/m/{page.pageid}/  
🔗 **Wikipedia:** https://en.wikipedia.org/wiki/{title.replace(" ", "_")}

Let me know if you want **more info** or **similar movies** 🙏✨
"""
        return response

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
            or image_info_response(prompt)
            or llm.invoke(st.session_state.messages).content
            or get_movie_info(prompt)
        )

        st.markdown(answer)
        st.session_state.messages.append(AIMessage(content=answer))

