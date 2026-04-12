import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import extract
from language import LANGUAGE_CODES, translate_text
from gtts import gTTS

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def chunk_text(text, max_tokens=3000, overlap=500):
    chunk_size = max_tokens * 4
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

def summarize_chunk(content, summary_type, max_output_tokens):
    prompt = f"Provide a {summary_type} summary of the following text:\n\n{content}"

    response = client.chat.completions.create(
        model="nvidia/llama-3.3-nemotron-super-49b-v1",
        messages=[
            {"role": "system", "content": "You are a helpful summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_output_tokens,
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

def summarize_file(full_text, summary_type):
    token_map = {"Brief": 500, "Detailed": 1024, "Important": 800}
    chunks = chunk_text(full_text)

    return "\n\n".join(
        summarize_chunk(chunk, summary_type, token_map[summary_type])
        for chunk in chunks
    )

def generate_audio(text, lang='en'):
    filename = "output.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

st.set_page_config(page_title="LINGUAVOX", layout="wide")

st.sidebar.header("Upload File")
uploaded_file = st.sidebar.file_uploader("Upload", type=["pdf", "txt", "docx", "pptx", "png", "jpg"])

mode = st.sidebar.selectbox("Mode", ["Summarize", "Full Text"])

enable_translation = st.sidebar.checkbox("Enable Translation")

target_lang = 'en'
if enable_translation:
    selected_lang = st.sidebar.selectbox("Language", list(LANGUAGE_CODES.keys()))
    target_lang = LANGUAGE_CODES[selected_lang]

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
        st.error("Unsupported file")
        st.stop()

    if mode == "Summarize":
        if st.button("Generate Summary"):
            summary = summarize_file(text, "Brief")

            if enable_translation:
                summary = translate_text(summary, target_lang)

            st.text_area("Summary", summary)

            if st.button("Play Audio"):
                audio = generate_audio(summary, target_lang)
                st.audio(audio)

    elif mode == "Full Text":
        if enable_translation:
            text = translate_text(text, target_lang)

        st.text_area("Text", text)

        if st.button("Play Audio"):
            audio = generate_audio(text, target_lang)
            st.audio(audio)