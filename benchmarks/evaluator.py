"""
PromptForge Multi-Metric Evaluation Engine
Evaluates compressed prompts across 6 dimensions.
"""

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


def calculate_constraint_preservation(required_constraints: list, compressed_text: str) -> float:
    """Fraction of required constraints found in compressed text."""
    if not required_constraints:
        return 1.0
    text_lower = compressed_text.lower()
    preserved = 0
    for constraint in required_constraints:
        # Check if the core idea of the constraint is preserved
        # Use word-level matching for robustness
        words = constraint.lower().split()
        # If 60%+ of the constraint words appear, consider it preserved
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.6, 1):
            preserved += 1
    return round(preserved / len(required_constraints), 4)


def calculate_feature_coverage(required_features: list, compressed_text: str) -> float:
    """Fraction of required features found in compressed text."""
    if not required_features:
        return 1.0
    text_lower = compressed_text.lower()
    covered = 0
    for feature in required_features:
        words = feature.lower().split()
        match_count = sum(1 for w in words if w in text_lower)
        if match_count >= max(len(words) * 0.5, 1):
            covered += 1
    return round(covered / len(required_features), 4)


def calculate_output_format_score(expected_format: str, compressed_text: str) -> float:
    """Checks if the compressed text preserves format indicators."""
    if not expected_format or expected_format == "plain_text":
        return 1.0

    text_lower = compressed_text.lower()

    format_indicators = {
        "json": ["json", "{", "}", ":", '"'],
        "markdown": ["#", "##", "-", "**", "```"],
        "code_block": ["```", "def ", "function ", "class ", "import ", "const "],
        "table": ["|", "table", "column", "row", "csv", "delimiter"]
    }

    indicators = format_indicators.get(expected_format, [expected_format])
    if not indicators:
        return 1.0

    found = sum(1 for ind in indicators if ind.lower() in text_lower)
    # Need at least 30% of indicators present
    score = min(found / max(len(indicators) * 0.3, 1), 1.0)
    return round(score, 4)


def calculate_keyword_preservation(important_keywords: list, compressed_text: str) -> float:
    """Fraction of important keywords preserved in compressed text."""
    if not important_keywords:
        return 1.0
    text_lower = compressed_text.lower()
    preserved = sum(1 for kw in important_keywords if kw.lower() in text_lower)
    return round(preserved / len(important_keywords), 4)


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


def calculate_final_score(token_reduction: float, constraint_score: float,
                          feature_score: float, format_score: float,
                          keyword_score: float) -> float:
    """Weighted final quality score."""
    weights = {
        "token_reduction": 0.15,
        "constraint": 0.30,
        "feature": 0.20,
        "format": 0.15,
        "keyword": 0.20
    }
    score = (
        weights["token_reduction"] * token_reduction +
        weights["constraint"] * constraint_score +
        weights["feature"] * feature_score +
        weights["format"] * format_score +
        weights["keyword"] * keyword_score
    )
    return round(score, 4)


def evaluate(original_text: str, compressed_text: str, benchmark_item: dict) -> dict:
    """
    Runs all evaluation metrics on a single compressed prompt.
    Returns a dictionary of all scores.
    """
    token_reduction = calculate_token_reduction(original_text, compressed_text)
    constraint_score = calculate_constraint_preservation(
        benchmark_item.get("required_constraints", []), compressed_text
    )
    feature_score = calculate_feature_coverage(
        benchmark_item.get("required_features", []), compressed_text
    )
    format_score = calculate_output_format_score(
        benchmark_item.get("expected_output_format", ""), compressed_text
    )
    keyword_score = calculate_keyword_preservation(
        benchmark_item.get("important_keywords", []), compressed_text
    )
    risk = calculate_risk_score(constraint_score, feature_score, format_score)
    final = calculate_final_score(token_reduction, constraint_score, feature_score, format_score, keyword_score)

    return {
        "original_tokens": estimate_tokens(original_text),
        "compressed_tokens": estimate_tokens(compressed_text),
        "token_reduction": token_reduction,
        "constraint_preservation": constraint_score,
        "feature_coverage": feature_score,
        "output_format_score": format_score,
        "keyword_preservation": keyword_score,
        "risk": risk,
        "final_score": final
    }