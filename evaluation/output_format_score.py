def calculate_output_format_score(output_req: dict, compressed_text: str) -> dict:
    """Returns score and missing format indicators."""
    if not output_req or not output_req.get("locked"):
        return {"score": 1.0, "missing_items": []}
        
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
        return {"score": 1.0, "missing_items": []}
        
    missing_indicators = [ind for ind in indicators if ind.lower() not in text_lower]
    found = len(indicators) - len(missing_indicators)
    
    score = round(min(found / max(len(indicators) * 0.3, 1), 1.0), 4)
    return {"score": score, "missing_items": missing_indicators}