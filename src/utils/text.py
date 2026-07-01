import re

def normalize_text(text):
    """
    Strips punctuation and condenses whitespace so BM25 tokenization is perfect.
    """
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
