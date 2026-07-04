"""
Section Relevance Scorer
Evaluates how relevant each parsed section is to the main task.
"""
from models.embedding_model import is_embedding_available, cosine_similarity_score

def fallback_rule_based_relevance(section_name: str) -> float:
    """
    Returns a hardcoded relevance score based on the section name.
    Used when the semantic engine is unavailable.
    """
    scores = {
        "constraints": 1.0,
        "task": 1.0,
        "output_format": 0.95,
        "features": 0.9,
        "context": 0.6,
        "examples": 0.5,
        "other": 0.3
    }
    return scores.get(section_name.lower(), 0.5)

def get_relevance_label(score: float) -> str:
    """Assigns a human-readable label based on the score threshold."""
    if score >= 0.85:
        return "critical"
    elif score >= 0.65:
        return "high"
    elif score >= 0.40:
        return "medium"
    else:
        return "low"

def score_section_relevance(section_name: str, section_text: str, task_text: str) -> float:
    """
    Calculates the relevance score for a single section.
    Uses embeddings if available, otherwise falls back to rule-based scores.
    """
    if is_embedding_available() and task_text.strip():
        score = cosine_similarity_score(section_text, task_text)
        if score is not None:
            return score
            
    # Fallback to rule-based if embeddings fail or task is empty
    return fallback_rule_based_relevance(section_name)

def score_all_sections(prompt_ir: dict) -> dict:
    """
    Iterates through all sections in the Prompt IR and adds 
    relevance_score and relevance_label to each.
    """
    task_text = prompt_ir.get("task", {}).get("text", "")
    
    for section in prompt_ir.get("sections", []):
        name = section.get("name", "other").lower()
        content = section.get("content", "")
        
        score = score_section_relevance(name, content, task_text)
        
        section["relevance_score"] = round(score, 4)
        section["relevance_label"] = get_relevance_label(score)
        
    return prompt_ir