def scan(text, forbidden):
    for term in forbidden:
        if term.lower() in text.lower():
            raise ValueError(f"Forbidden term detected: {term}")
