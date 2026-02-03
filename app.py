import streamlit as st
import requests
from datetime import datetime
import pytz
import uuid
from PIL import Image
import io
import base64

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

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

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

# ---------------- IMAGE CAPTION MODEL ----------------
@st.cache_resource
def load_caption_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

image_processor, image_model = load_caption_model()

# ---------------- TEXT TO IMAGE (HF API) ----------------
def generate_image_hf(prompt):
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {
        "Authorization": f"Bearer {st.secrets['HF_API_KEY']}"
    }
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt},
        timeout=60
    )
    return Image.open(io.BytesIO(response.content))

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🧠 NeoMind AI")
    st.divider()

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
            st.warning("Voice not clear")

    uploaded_image = st.file_uploader(
        "🖼️ Upload Image",
        type=["jpg", "jpeg", "png"]
    )

    st.divider()

    st.markdown("### 🎨 Create Image")
    image_prompt = st.text_input(
        "Describe the image",
        placeholder="A futuristic robot reading a book"
    )

    create_image = st.button("🖌️ Create Image")

    st.divider()
    temperature = st.slider("Creativity", 0.0, 1.0, 0.5)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages.clear()
        st.session_state.image_caption = None
        st.session_state.image_id = None
        st.session_state.generated_image = None
        st.session_state.voice_text = ""
        st.rerun()

    st.caption("Created by **Shashank N P**")

# ---------------- LLM ----------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=temperature
)

# ---------------- HEADER ----------------
st.markdown("<h2 style='text-align:center'>💬 NeoMind AI</h2>", unsafe_allow_html=True)

# ---------------- IMAGE CAPTION ----------------
if uploaded_image:
    image_key = uploaded_image.name + str(uploaded_image.size)

    if image_key != st.session_state.image_id:
        image = Image.open(uploaded_image).convert("RGB")
        inputs = image_processor(image, return_tensors="pt")
        output = image_model.generate(**inputs)
        caption = image_processor.decode(output[0], skip_special_tokens=True)

        st.session_state.image_caption = caption
        st.session_state.image_id = image_key

        st.session_state.messages.append(
            AIMessage(content=f"🖼️ **Image detected:** {caption}")
        )
        st.rerun()

# ---------------- TEXT TO IMAGE ----------------
if create_image and image_prompt.strip():
    with st.spinner("Creating image..."):
        img = generate_image_hf(image_prompt)

    st.session_state.generated_image = img

    st.session_state.messages.append(
        HumanMessage(content=f"Create image: {image_prompt}")
    )
    st.session_state.messages.append(
        AIMessage(content="__IMAGE__")
    )
    st.rerun()

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        if msg.content == "__IMAGE__":
            st.image(st.session_state.generated_image, use_container_width=True)
        else:
            st.markdown(msg.content)

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask NeoMind AI anything…")

if prompt or st.session_state.voice_text:
    user_text = prompt if prompt else st.session_state.voice_text
    st.session_state.voice_text = ""

    st.session_state.messages.append(HumanMessage(content=user_text))

    answer = smart_answer(user_text)

    if not answer and st.session_state.image_caption:
        if "image" in user_text.lower():
            answer = llm.invoke(
                f"Explain this image: {st.session_state.image_caption}"
            ).content

    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.session_state.messages.append(AIMessage(content=answer))
    st.rerun()
