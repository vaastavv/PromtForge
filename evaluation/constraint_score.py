def calculate_constraint_preservation(constraints: list, compressed_text: str) -> dict:
    """Returns score and list of missing constraint texts."""
    if not constraints:
        return {"score": 1.0, "missing_items": []}
    
    text_lower = compressed_text.lower()
    preserved = 0
    missing = []
    
    for c in constraints:
        text = c.get("text", "")
        words = text.lower().split()
        if not words:
            continue
            
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.6, 1):
            preserved += 1
        else:
            missing.append(text)
            
    score = round(preserved / len(constraints), 4)
    return {"score": score, "missing_items": missing}