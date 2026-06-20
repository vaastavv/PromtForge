from typing import Dict, List, Any

# Keyword dictionaries for rule-based classification
KEYWORDS = {
    "constraints": [
        "must", "should", "cannot", "can't", "do not", "don't", "without", 
        "no api", "api key", "free", "offline", "local", "8gb", "ram", 
        "preserve", "don't miss", "no paid", "strictly", "requirement", "rule"
    ],
    "features": [
        "include", "add", "feature", "support", "module", "architecture", 
        "evaluation", "dashboard", "visualization", "compression", "prompt ir", 
        "tokenizer", "benchmark", "ollama", "llmlingua", "functionality"
    ],
    "output_format": [
        "give me", "return", "output", "format", "table", "json", "markdown", 
        "step-by-step", "architecture diagram", "plan", "strictly in", "structure"
    ],
    "examples": [
        "example", "sample", "for instance", "e.g.", "like this", "such as"
    ],
    "task": [
        "build", "create", "design", "make", "develop", "implement", 
        "generate", "write", "solve", "analyze", "optimize"
    ]
}

# Priority order: If a line matches multiple categories, which one wins?
# Constraints are the most critical, so they have the highest priority.
PRIORITY_ORDER = ["constraints", "output_format", "features", "examples", "task"]

def parse_sections(preprocessed_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Classifies cleaned lines into logical sections based on keyword detection.
    """
    lines = preprocessed_data.get("lines", [])
    
    # Initialize the parsed structure
    parsed = {
        "task": [],
        "constraints": [],
        "features": [],
        "output_format": [],
        "context": [],
        "examples": [],
        "other": []
    }

    for line in lines:
        # Skip completely blank lines
        if not line.strip():
            continue

        line_lower = line.lower()
        matched_category = "context"  # Default bucket for background info
        matched_kws = []

        # Check against high-priority categories first
        for category in PRIORITY_ORDER:
            kws = [kw for kw in KEYWORDS[category] if kw in line_lower]
            if kws:
                matched_category = category
                matched_kws = kws
                break  # Stop checking once we find the highest priority match

        # If no priority keywords matched, check if it's just a short filler line
        if matched_category == "context" and len(line.split()) < 4:
            matched_category = "other"

        # Add to the parsed dictionary
        parsed[matched_category].append({
            "text": line,
            "matched_keywords": matched_kws
        })

    return parsed