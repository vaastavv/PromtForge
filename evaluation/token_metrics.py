def estimate_tokens(text: str) -> int:
    """MVP token estimation: word_count * 1.3"""
    if not text or not text.strip():
        return 0
    return int(len(text.split()) * 1.3)

def calculate_token_reduction(original_text: str, compressed_text: str) -> float:
    """Percentage of tokens removed."""
    orig = estimate_tokens(original_text)
    comp = estimate_tokens(compressed_text)
    if orig == 0:
        return 0.0
    return round((orig - comp) / orig, 4)
