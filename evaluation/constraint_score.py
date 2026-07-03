def calculate_constraint_preservation(constraints: list, compressed_text: str) -> float:
    """Fraction of required constraints found in compressed text."""
    if not constraints:
        return 1.0
    
    text_lower = compressed_text.lower()
    preserved = 0
    
    for c in constraints:
        text = c.get("text", "")
        words = text.lower().split()
        if not words:
            continue
            
        # If 60%+ of the constraint words appear, consider it preserved
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.6, 1):
            preserved += 1
            
    return round(preserved / len(constraints), 4)