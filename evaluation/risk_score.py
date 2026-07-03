def calculate_risk_score(constraint_score: float, feature_score: float, format_score: float) -> str:
    """Determines risk level based on preservation scores."""
    if constraint_score < 1.0:
        return "High"
    elif feature_score < 0.8:
        return "Medium"
    elif format_score < 0.9:
        return "Medium"
    else:
        return "Low"