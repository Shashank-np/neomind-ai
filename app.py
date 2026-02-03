import streamlit as st
import requests
from datetime import datetime
import pytz
import uuid
from PIL import Image

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

from transformers import BlipProcessor, BlipForConditionalGeneration

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
section[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 10px;
}
section[data-testid="stAudioInput"] {
    padding: 2px !important;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "audio_key" not in st.session_state:
    st.session_state.audio_key = str(uuid.uuid4())

if "image_caption" not in st.session_state:
    st.session_state.image_caption = None

if "image_id" not in st.session_state:
    st.session_state.image_id = None

# ---------------- TIMEZONE ----------------
@st.cache_data(ttl=3600)
def get_timezone():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=3).json()
        return pytz.timezone(res.get("timezone", "UTC"))
    except:
        return pytz.UTC

tz = get_timezone()

# ---------------- SMART ANSWERS ----------------
def smart_answer(text):
    now = datetime.now(tz)
    t = text.lower().strip()

    if t in ["time", "current time"]:
        return f"⏰ {now.strftime('%I:%M %p')}"

    if "today" in t:
        return f"📅 {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- IMAGE MODEL ----------------
@st.cache_resource
def load_image_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

image_processor, image_model = load_image_model()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🧠 NeoMind AI")
    st.divider()

    # ---- VOICE INPUT ----
    audio = st.audio_input("🎙️ Speak", key=st.session_state.audio_key)

    if audio:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(audio) as source:
                data = r.record(source)
            st.session_state.voice_text = r.recognize_google(data)
            st.session_state.audio_key = str(uuid.uuid4())
        except:
            st.warning("Could not understand voice")

    # ---- IMAGE INPUT ----
    uploaded_image = st.file_uploader(
        "🖼️ Upload Image",
        type=["jpg", "jpeg", "png"]
    )

    st.divider()

    temperature = st.slider("🎨 Creativity", 0.0, 1.0, 0.5)

    # ---- CLEAR CHAT ----
    if st.button("🧹 Clear Chat"):
        st.session_state.messages.clear()
        st.session_state.image_caption = None
        st.session_state.image_id = None
        st.session_state.voice_text = ""
        st.rerun()

    st.divider()

    # ---------------- FEEDBACK BOX ----------------
    st.markdown("### 🆘 Feedback")

    feedback = st.text_area(
        "Your feedback",
        placeholder="Tell us what you like or what we can improve…",
        height=90
    )

    if st.button("📨 Send Feedback"):
        if feedback.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"feedback": feedback},
                    timeout=5
                )
                st.success("Thanks for your feedback 🙌")
            except:
                st.error("Failed to send feedback")
        else:
            st.warning("Please write some feedback")

    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown("<h2 style='text-align:center'>💬 NeoMind AI</h2>", unsafe_allow_html=True)

# ---------------- IMAGE PROCESS (IMMEDIATE RESPONSE) ----------------
if uploaded_image:
    current_image_id = uploaded_image.name + str(uploaded_image.size)

    if current_image_id != st.session_state.image_id:
        image = Image.open(uploaded_image).convert("RGB")
        inputs = image_processor(image, return_tensors="pt")
        output = image_model.generate(**inputs)
        caption = image_processor.decode(output[0], skip_special_tokens=True)

        st.session_state.image_caption = caption
        st.session_state.image_id = current_image_id

        st.session_state.messages.append(
            AIMessage(content=f"🖼️ **Image detected:** {caption}")
        )
        st.rerun()

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt or st.session_state.voice_text:
    user_text = prompt if prompt else st.session_state.voice_text
    st.session_state.voice_text = ""

    st.session_state.messages.append(HumanMessage(content=user_text))

    answer = smart_answer(user_text)

    if not answer and st.session_state.image_caption:
        if any(k in user_text.lower() for k in ["image", "photo", "picture", "this"]):
            detail_prompt = f"Describe this image in detail: {st.session_state.image_caption}"
            answer = llm.invoke(detail_prompt).content

    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(AIMessage(content=answer))
    st.rerun()
