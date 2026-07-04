def calculate_final_score(token_reduction: float, constraint_score: float, 
                          feature_score: float, format_score: float, 
                          keyword_score: float, semantic_score: float = None) -> float:
    """
    Weighted final quality score.
    Dynamically adjusts weights based on whether semantic similarity is available.
    """
    if semantic_score is None:
        # Phase 1 Rule-Based Weights (Total: 100%)
        weights = {
            "token_reduction": 0.15, 
            "constraint": 0.30, 
            "feature": 0.25, 
            "format": 0.15, 
            "keyword": 0.15
        }
        return round(
            weights["token_reduction"] * token_reduction +
            weights["constraint"] * constraint_score +
            weights["feature"] * feature_score +
            weights["format"] * format_score +
            weights["keyword"] * keyword_score, 4
        )
    else:
        # Phase 2 Semantic Weights (Total: 100%)
        weights = {
            "token_reduction": 0.10, 
            "constraint": 0.25, 
            "feature": 0.20, 
            "format": 0.15, 
            "keyword": 0.15,
            "semantic": 0.15
        }
        return round(
            weights["token_reduction"] * token_reduction +
            weights["constraint"] * constraint_score +
            weights["feature"] * feature_score +
            weights["format"] * format_score +
            weights["keyword"] * keyword_score +
            weights["semantic"] * semantic_score, 4
        )