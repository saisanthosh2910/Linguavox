from deep_translator import GoogleTranslator
import textwrap

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese (Simplified)": "zh-cn"
}

def chunk_text(text, max_length=3000):
    return textwrap.wrap(text, width=max_length, break_long_words=False)

def translate_text(text, dest_lang='te'):
    if not text.strip():
        return ""

    chunks = chunk_text(text)
    translated_chunks = []

    for chunk in chunks:
        try:
            translated = GoogleTranslator(source='auto', target=dest_lang).translate(chunk)
            translated_chunks.append(translated)
        except Exception:
            translated_chunks.append("[Translation Error]")

    return " ".join(translated_chunks)