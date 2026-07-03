def calculate_final_score(token_reduction: float, constraint_score: float, 
                          feature_score: float, format_score: float, 
                          keyword_score: float) -> float:
    """Weighted final quality score."""
    weights = {
        "token_reduction": 0.15,
        "constraint": 0.30,
        "feature": 0.25,
        "format": 0.15,
        "keyword": 0.15
    }
    
    score = (
        weights["token_reduction"] * token_reduction +
        weights["constraint"] * constraint_score +
        weights["feature"] * feature_score +
        weights["format"] * format_score +
        weights["keyword"] * keyword_score
    )
    return round(score, 4)