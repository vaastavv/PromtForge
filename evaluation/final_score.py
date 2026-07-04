def calculate_final_score(token_reduction: float, constraint_score: float, 
                          feature_score: float, format_score: float, 
                          keyword_score: float, semantic_score: float = -1.0) -> float:
    """
    Weighted final quality score.
    Automatically falls back to rule-based weights if semantic_score is -1.0.
    """
    if semantic_score < 0:
        # Phase 1 Fallback Weights
        weights = {
            "token_reduction": 0.15, "constraint": 0.30, "feature": 0.25, 
            "format": 0.15, "keyword": 0.15
        }
        return round(
            weights["token_reduction"] * token_reduction +
            weights["constraint"] * constraint_score +
            weights["feature"] * feature_score +
            weights["format"] * format_score +
            weights["keyword"] * keyword_score, 4
        )
    else:
        # Phase 2 Semantic Weights
        weights = {
            "token_reduction": 0.10, "constraint": 0.20, "feature": 0.15, 
            "format": 0.10, "keyword": 0.10, "semantic": 0.35
        }
        return round(
            weights["token_reduction"] * token_reduction +
            weights["constraint"] * constraint_score +
            weights["feature"] * feature_score +
            weights["format"] * format_score +
            weights["keyword"] * keyword_score +
            weights["semantic"] * semantic_score, 4
        )