"""
Advanced Compression Planner
Assigns specific compression actions to sections based on IR, relevance, and mode.
"""

def determine_action(section: dict, mode: str) -> str:
    """Determines the compression action for a single section."""
    name = section.get("name", "other").lower()
    locked = section.get("locked", False)
    relevance = section.get("relevance_score", 0.5)
    label = section.get("relevance_label", "medium")
    
    # 1. Absolute Rules (Apply to all modes)
    if locked and name in ["task", "constraints", "output_format"]:
        return "preserve"
    if locked and name == "features":
        return "compress_lightly"
    if name == "examples" and locked:
        return "preserve"

    # 2. Mode-Specific Rules
    if mode == "safe":
        if name in ["context", "other"]:
            return "remove_duplicates"
        return "compress_lightly" # Default safe action
        
    elif mode == "balanced":
        if name == "context":
            return "summarize" if label in ["critical", "high"] else "compress_aggressively"
        if name == "examples":
            return "compress_aggressively"
        if name == "other" and relevance < 0.4:
            return "remove_if_low_value"
        return "compress_lightly"
        
    elif mode == "aggressive":
        if name == "context":
            return "compress_aggressively"
        if name in ["examples", "other"]:
            return "remove_if_low_value" if relevance < 0.5 else "compress_aggressively"
        return "compress_lightly"
        
    elif mode == "research":
        # Research mode behaves like balanced but logs heavily
        if name == "context":
            return "summarize" if label in ["critical", "high"] else "compress_aggressively"
        if name == "examples":
            return "compress_aggressively"
        return "compress_lightly"

    return "compress_lightly" # Fallback

def plan_compression(prompt_ir: dict) -> dict:
    """
    Iterates through all sections and assigns a compression_action.
    In 'research' mode, it logs the reasoning to traceability.
    """
    mode = prompt_ir.get("compression_policy", {}).get("mode", "balanced")
    traceability = prompt_ir.get("traceability", {})
    plan_log = traceability.get("compression_plan_log", [])
    
    for section in prompt_ir.get("sections", []):
        action = determine_action(section, mode)
        section["compression_action"] = action
        
        # Research mode logging
        if mode == "research":
            reason = f"Section '{section['name']}' assigned '{action}' due to mode={mode}, locked={section.get('locked')}, relevance={section.get('relevance_score')}"
            plan_log.append(reason)
            
    traceability["compression_plan_log"] = plan_log
    prompt_ir["traceability"] = traceability
    
    return prompt_ir