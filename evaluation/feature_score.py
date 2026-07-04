def calculate_feature_coverage(features: list, compressed_text: str) -> dict:
    """Returns score and list of missing feature names."""
    if not features:
        return {"score": 1.0, "missing_items": []}
        
    text_lower = compressed_text.lower()
    covered = 0
    missing = []
    
    for f in features:
        name = f.get("name", "")
        words = name.lower().split()
        if not words:
            continue
            
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.5, 1):
            covered += 1
        else:
            missing.append(name)
            
    score = round(covered / len(features), 4)
    return {"score": score, "missing_items": missing}