import re

def tts_safe_text(text: str) -> str:
    """
    Converts ALL CAPS or oddly formatted brand names
    into TTS-friendly spoken text.
    """
    if not text:
        return text

    # If mostly uppercase, convert to title case
    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

    if uppercase_ratio > 0.6:
        text = text.title()

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
