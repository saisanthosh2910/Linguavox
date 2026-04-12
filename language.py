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

def chunk_text(text, size=3000):
    return textwrap.wrap(text, width=size)

def translate_text(text, dest_lang):
    chunks = chunk_text(text)
    translated = []

    for chunk in chunks:
        try:
            translated.append(
                GoogleTranslator(source='auto', target=dest_lang).translate(chunk)
            )
        except:
            translated.append("[Error]")

    return " ".join(translated)