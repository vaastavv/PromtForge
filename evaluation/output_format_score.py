def calculate_output_format_score(output_req: dict, compressed_text: str) -> float:
    """Checks if the compressed text preserves format indicators."""
    if not output_req or not output_req.get("locked"):
        return 1.0
        
    format_str = output_req.get("format", "plain_text").lower()
    text_lower = compressed_text.lower()
    
    format_indicators = {
        "json": ["json", "{", "}", ":"],
        "markdown": ["#", "##", "-", "**"],
        "code_block": ["```", "def ", "function ", "class ", "import "],
        "table": ["|", "table", "column", "row"],
        "plain_text": []
    }
    
    indicators = format_indicators.get(format_str, [format_str])
    if not indicators:
        return 1.0
        
    found = sum(1 for ind in indicators if ind.lower() in text_lower)
    # Need at least 30% of indicators present
    score = min(found / max(len(indicators) * 0.3, 1), 1.0)
    return round(score, 4)