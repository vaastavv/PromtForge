def calculate_feature_coverage(features: list, compressed_text: str) -> float:
    """Fraction of required features found in compressed text."""
    if not features:
        return 1.0
        
    text_lower = compressed_text.lower()
    covered = 0
    
    for f in features:
        name = f.get("name", "")
        words = name.lower().split()
        if not words:
            continue
            
        # If 50%+ of the feature words appear, consider it covered
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.5, 1):
            covered += 1
            
    return round(covered / len(features), 4)