import streamlit as st
import requests
from datetime import datetime
import pytz
import uuid

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# IMAGE CAPTIONING (STREAMLIT CLOUD SAFE)
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

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
    padding: 12px;
}
section[data-testid="stAudioInput"] {
    padding: 4px !important;
    margin: 0 !important;
}
.sidebar-logo {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    margin-top: 10px;
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

# image control
if "image_caption" not in st.session_state:
    st.session_state.image_caption = None

if "image_detailed" not in st.session_state:
    st.session_state.image_detailed = None

if "image_processed" not in st.session_state:
    st.session_state.image_processed = False

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
def smart_answer(prompt):
    text = prompt.lower().strip()
    now = datetime.now(tz)

    if text in ["time", "current time", "what is the time"]:
        return f"⏰ Current time: {now.strftime('%I:%M %p')}"

    if "today" in text:
        return f"📅 Today: {now.strftime('%d %B %Y')} ({now.strftime('%A')})"

    return None

# ---------------- IMAGE MODEL ----------------
@st.cache_resource
def load_image_model():
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )
    return processor, model

image_processor, image_model = load_image_model()

# ---------------- SIDEBAR ----------------
with st.sidebar:

    # 1️⃣ VOICE + IMAGE INPUT (ONE BOX)
    st.subheader("🎙️ Voice / 🖼️ Image Input")

    audio = st.audio_input(
        "Speak",
        key=st.session_state.audio_key,
        label_visibility="collapsed"
    )

    uploaded_image = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

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

    # 2️⃣ LOGO BELOW INPUT
    st.markdown("<div class='sidebar-logo'>🧠 NeoMind AI</div>", unsafe_allow_html=True)

    # 3️⃣ LINE
    st.divider()

    # 4️⃣ CREATIVITY
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

    # 5️⃣ CLEAR CHAT
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.voice_text = ""
        st.session_state.image_caption = None
        st.session_state.image_detailed = None
        st.session_state.image_processed = False
        st.rerun()

    # 6️⃣ LINE
    st.divider()

    # 7️⃣ FEEDBACK
    st.subheader("🆘 Feedback")
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
                st.success("Thanks for your feedback!")
            except:
                st.error("Failed to send feedback.")

    # 8️⃣ CREATED BY
    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center'>💬 NeoMind AI</h1>", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------- IMAGE PROCESS (ONLY ONCE) ----------------
if uploaded_image and not st.session_state.image_processed:
    image = Image.open(uploaded_image).convert("RGB")
    inputs = image_processor(image, return_tensors="pt")
    out = image_model.generate(**inputs)
    caption = image_processor.decode(out[0], skip_special_tokens=True)

    st.session_state.image_caption = caption
    st.session_state.image_processed = True

    st.session_state.messages.append(
        AIMessage(content=f"🖼️ I see: **{caption}**")
    )

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt or st.session_state.voice_text:
    user_text = prompt if prompt else st.session_state.voice_text
    st.session_state.voice_text = ""

    st.session_state.messages.append(HumanMessage(content=user_text))

    answer = smart_answer(user_text)

    if not answer and st.session_state.image_caption:
        if any(k in user_text.lower() for k in ["detail", "explain", "describe", "more"]):
            if not st.session_state.image_detailed:
                detail_prompt = (
                    f"The image shows: {st.session_state.image_caption}. "
                    f"Explain this image in detail."
                )
                detailed = llm.invoke(detail_prompt).content
                st.session_state.image_detailed = detailed

                answer = (
                    detailed +
                    f"\n\n📌 **In short:** {st.session_state.image_caption}"
                )
            else:
                answer = "I already explained the image. Ask something else 🙂"

    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(AIMessage(content=answer))
    st.rerun()
