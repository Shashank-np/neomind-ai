import streamlit as st
import requests
from datetime import datetime
import pytz
import wikipedia
from bs4 import BeautifulSoup
from pydub import AudioSegment
from google.cloud import speech
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="NeoMind AI", page_icon="🧠", layout="wide")

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
            return f"🌐 From the web:\n\n{snippet.text}"
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
        🖼️ {page.title}
        {summary} 🔗 https://commons.wikimedia.org/wiki/{page.title.replace(" ", "_")} """
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
        "Share your feedback",
        placeholder="Tell us what to improve..."
    )

    if st.button("Send Feedback"):
        if feedback.strip():
            try:
                requests.post(
                    "https://formspree.io/f/xblanbjk",
                    data={"message": feedback},
                    timeout=5
                )
                st.success("✅ Feedback sent")
            except:
                st.error("❌ Failed to send feedback")
        else:
            st.warning("⚠️ Please write feedback")

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

# Add microphone button
with st.form('voice_input_form', clear_on_submit=True):
    st.write("")
    voice_input_button = st.form_submit_button(label="Listen", key='listen_button')

if voice_input_button:
    # Upload audio file
    file_uploader = st.file_uploader(label="Upload audio file:")
    if file_uploader:
        if file_uploader.type == 'audio/wav':
            audio_data = file_uploader.getvalue()
            audio_segment = AudioSegment(
                data=audio_data,
                format="wav",
                sample_width=2,
                frame_rate=16000,
                channels=1
            )
            audio_chunks = []
            chunk_length_ms = 10 * 1000  # 10 seconds
            n chunks = len(audio_segment) / chunk_length_ms
            for i in range(int(n_chunks)):
                start_index = i * chunk_length_ms
                end_index = start_index + chunk_length_ms
                audio_chunk = audio_segment[start_index:end_index]
                audio_chunks.append(
                    speech.types.RecognitionConfig(
                        encoding=speech.Encoding.LINEAR16,
                        sample_rate_hertz=16000,
                        language_code="en-US"
                    )
                )

            client = speech.SpeechClient()
            operations = []
            for i, chunk in enumerate(audio_chunks):
                response = client.long_running_recognition(
                    requests=[speech.types.RecognitionConfig(
                        encoding=speech.Encoding.LINEAR16,
                        sample_rate_hertz=16000,
                        language_code="en-US"
                    )], 
                    audio_input={
                        "uri": "gs://my-bucket/my-media-file.wav",
                        "content": chunk.raw_data
                    }, 
                )
                operations.append(response.operation)

            # Get recognition results
            response = speech.types.LongRunningRecognitionResponse()
            for i, op in enumerate(operations):
                result = op.get(result=speech.types.RecognitionResult())
                response.final = result.results[-1]
            transcript = response.final.alternatives[0].transcript

            # Add transcript to chat
            st.session_state.messages.append(HumanMessage(content=transcript))

# ---------------- ORIGINAL INPUT ----------------
prompt = st.text_input('Ask NeoMind AI anything...', max_chars=200)
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

# Add microphone button
with st.container():
    st.write("")
    microphone_button = st.button(label="🎙️", key='microphone_button')
    if microphone_button:
        # Recognize voice input
        # Upload audio file
        file_uploader = st.file_uploader(label="Upload audio file:")
        if file_uploader:
            if file_uploader.type == 'audio/wav':
                audio_data = file_uploader.getvalue()
                audio_segment = AudioSegment(
                    data=audio_data,
                    format="wav",
                    sample_width=2,
                    frame_rate=16000,
                    channels=1
                )
                audio_chunks = []
                chunk_length_ms = 10 * 1000  # 10 seconds
                n_chunks = len(audio_segment) / chunk_length_ms
                for i in range(int(n_chunks)):
                    start_index = i * chunk_length_ms
                    end_index = start_index + chunk_length_ms
                    audio_chunk = audio_segment[start_index:end_index]
                    audio_chunks.append(
                        speech.types.RecognitionConfig(
                            encoding=speech.Encoding.LINEAR16,
                            sample_rate_hertz=16000,
                            language_code="en-US"
                        )
                    )

                client = speech.SpeechClient()
                operations = []
                for i, chunk in enumerate(audio_chunks):
                    response = client.long_running_recognition(
                        requests=[speech.types.RecognitionConfig(
                            encoding=speech.Encoding.LINEAR16,
                            sample_rate_hertz=16000,
                            language_code="en-US"
                        )], 
                        audio_input={
                            "uri": "gs://my-bucket/my-media-file.wav",
                            "content": chunk.raw_data
                        }, 
                    )
                    operations.append(response.operation)

                # Get recognition results
                response = speech.types.LongRunningRecognitionResponse()
                for i, op in enumerate(operations):
                    result = op.get(result=speech.types.RecognitionResult())
                    response.final = result.results[-1]
                transcript = response.final.alternatives[0].transcript

                # Add transcript to chat
                st.session_state.messages.append(HumanMessage(content=transcript))

# ---------------- CHAT HANDLER ----------------
with st.container():
    answer = (
        smart_answer(prompt)
        or image_info_response(prompt)
        or web_scrape_summary(prompt)
    )

    if not answer:
        answer = llm.invoke(st.session_state.messages).content

    st.write("")
    st.markdown(answer)
    st.session_state.messages.append(AIMessage(content=answer))
