import streamlit as st
import requests
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------- KEYS ----------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
MAP_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# ---------------- PAGE ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION ----------------
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

# ---------------- LOCATION (IP BASED) ----------------
def get_user_location():
    try:
        data = requests.get("https://ipinfo.io/json").json()
        city = data.get("city")
        loc = data.get("loc")
        if city and loc:
            lat, lng = loc.split(",")
            return city, lat, lng
    except:
        pass
    return None, None, None

# ---------------- GOOGLE MAPS BAR SEARCH ----------------
def get_nearby_bars(lat, lng):
    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius=5000&type=bar&key={MAP_KEY}"
    )
    res = requests.get(url).json()
    bars = []

    for place in res.get("results", [])[:5]:
        bars.append(
            f"- **{place['name']}** ⭐ {place.get('rating','N/A')} | {place.get('vicinity','')}"
        )
    return bars

# ---------------- SMART HANDLER ----------------
def smart_answer(prompt):
    text = prompt.lower()

    if "bar" in text:
        city, lat, lng = get_user_location()
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")

        if not lat:
            return "❌ Unable to detect your location. Please allow location access."

        bars = get_nearby_bars(lat, lng)

        if not bars:
            return f"❌ No bars found near **{city}**."

        return f"""
🍺 **Best Bars Near You ({city})**
🕒 *As of {now}*

{chr(10).join(bars)}

📍 Powered by Google Maps
"""

    return None

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
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

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

# ---------------- CHAT ----------------
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
                0, SystemMessage(content="You are NeoMind AI. Be accurate and factual.")
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
