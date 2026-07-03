def extract_keywords(prompt_ir: dict) -> list:
    """Extracts important keywords from constraints, features, and task."""
    keywords = []
    
    for c in prompt_ir.get("constraints", []):
        keywords.extend(c.get("text", "").lower().split())
    for f in prompt_ir.get("features", []):
        keywords.extend(f.get("name", "").lower().split())
        
    task_text = prompt_ir.get("task", {}).get("text", "").lower()
    keywords.extend(task_text.split())
    
    # Remove very short words (like 'a', 'to', 'in') and duplicates
    keywords = list(set([k for k in keywords if len(k) > 3]))
    return keywords

def calculate_keyword_preservation(keywords: list, compressed_text: str) -> float:
    """Fraction of important keywords preserved in compressed text."""
    if not keywords:
        return 1.0
        
    text_lower = compressed_text.lower()
    preserved = sum(1 for kw in keywords if kw in text_lower)
    return round(preserved / len(keywords), 4)