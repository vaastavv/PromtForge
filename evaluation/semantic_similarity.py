"""
Semantic Similarity Evaluator
Calculates the cosine similarity between original and optimized prompts.
"""
from models.embedding_model import is_embedding_available, cosine_similarity_score

def calculate_semantic_similarity(original_text: str, optimized_text: str) -> dict:
    """
    Calculates semantic similarity and returns a structured dictionary.
    """
    # 1. Check if the engine is available
    if not is_embedding_available():
        return {
            "available": False,
            "score": None,
            "label": "Unavailable",
            "warning": "Semantic engine is disabled or libraries are not installed."
        }
    
    # 2. Calculate score
    score = cosine_similarity_score(original_text, optimized_text)
    
    # 3. Determine label based on thresholds
    if score >= 0.88:
        label = "High"
        warning = ""
    elif score >= 0.75:
        label = "Medium"
        warning = "Meaning is mostly preserved, but some nuance may have been lost."
    else:
        label = "Low"
        warning = "Significant semantic drift detected. The optimized prompt may have lost core intent."
        
    return {
        "available": True,
        "score": score,
        "label": label,
        "warning": warning
    }