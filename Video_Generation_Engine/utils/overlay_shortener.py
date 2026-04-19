def short_overlay(text: str, max_words: int = 2) -> str:
    """
    Converts a feature sentence into a short, clean,
    2-word visual overlay suitable for fast video consumption.
    """

    if not text:
        return ""

    stopwords = {
        "with", "for", "and", "to", "of", "the",
        "made", "contains", "includes", "provides",
        "support", "supporting", "helps", "help",
        "high", "quality"
    }

    words = [
        w.capitalize()
        for w in text.split()
        if w.lower() not in stopwords
    ]

    # Take first 2 meaningful words
    return " ".join(words[:max_words])
