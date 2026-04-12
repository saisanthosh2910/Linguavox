import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import extract
from language import LANGUAGE_CODES, translate_text
from gtts import gTTS

# Load env
load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

# ---------------- TEXT CHUNKING ----------------
def chunk_text(text, size=3000):
    return [text[i:i+size] for i in range(0, len(text), size)]

# ---------------- SUMMARIZATION ----------------
def summarize_text(text):
    chunks = chunk_text(text)
    summary = ""

    for chunk in chunks:
        response = client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1",
            messages=[
                {"role": "system", "content": "Summarize the text clearly."},
                {"role": "user", "content": chunk}
            ],
            max_tokens=500
        )
        summary += response.choices[0].message.content + "\n\n"

    return summary

# ---------------- AUDIO ----------------
def generate_audio(text, lang='en'):
    file_path = "output.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(file_path)
    return file_path

# ---------------- UI ----------------
st.set_page_config(page_title="Linguavox", layout="wide")

st.title("🧠 Linguavox - AI Document Assistant")

uploaded_file = st.file_uploader("Upload file", type=["pdf", "txt", "docx", "pptx", "png", "jpg"])

mode = st.selectbox("Select Mode", ["Full Text", "Summarize"])

enable_translation = st.checkbox("Enable Translation")

target_lang = "en"
if enable_translation:
    lang_choice = st.selectbox("Select Language", list(LANGUAGE_CODES.keys()))
    target_lang = LANGUAGE_CODES[lang_choice]

# ---------------- PROCESS ----------------
if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()

    if file_ext == "pdf":
        text = extract.extract_text_from_pdf(uploaded_file)
    elif file_ext == "txt":
        text = extract.extract_text_from_txt(uploaded_file)
    elif file_ext == "docx":
        text = extract.extract_text_from_docx(uploaded_file)
    elif file_ext == "pptx":
        text = extract.extract_text_from_pptx(uploaded_file)
    elif file_ext in ["png", "jpg"]:
        text = extract.extract_text_from_image(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    if mode == "Full Text":
        if enable_translation:
            text = translate_text(text, target_lang)

        st.text_area("Output Text", text, height=300)

        if st.button("🔊 Play Audio"):
            audio = generate_audio(text, target_lang)
            st.audio(audio)

    elif mode == "Summarize":
        if st.button("Generate Summary"):
            summary = summarize_text(text)

            if enable_translation:
                summary = translate_text(summary, target_lang)

            st.text_area("Summary", summary, height=300)

            if st.button("🔊 Play Summary Audio"):
                audio = generate_audio(summary, target_lang)
                st.audio(audio)