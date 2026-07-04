"""
Adaptive Repair Engine
Surgically restores missing critical elements into the optimized prompt.
"""
import re

def repair_missing_constraints(text: str, missing_items: list) -> tuple:
    """Injects missing constraints into the Constraints section."""
    if not missing_items:
        return text, []
        
    restored = []
    injection = "\n".join([f"- [RESTORED] {item}" for item in missing_items]) + "\n"
    
    # Try to find existing Constraints section
    pattern = re.compile(r"(^Constraints:\s*\n?)", re.MULTILINE | re.IGNORECASE)
    if pattern.search(text):
        text = pattern.sub(rf"\1{injection}", text, count=1)
    else:
        # Create section if it doesn't exist
        text += f"\n\nConstraints:\n{injection}"
        
    for item in missing_items:
        restored.append(f"Restored constraint: {item}")
    return text, restored

def repair_missing_features(text: str, missing_items: list) -> tuple:
    """Injects missing features into the Required Features section."""
    if not missing_items:
        return text, []
        
    restored = []
    injection = "\n".join([f"- [RESTORED] {item}" for item in missing_items]) + "\n"
    
    pattern = re.compile(r"(^Required Features:\s*\n?)", re.MULTILINE | re.IGNORECASE)
    if pattern.search(text):
        text = pattern.sub(rf"\1{injection}", text, count=1)
    else:
        text += f"\n\nRequired Features:\n{injection}"
        
    for item in missing_items:
        restored.append(f"Restored feature: {item}")
    return text, restored

def repair_missing_output_requirements(text: str, missing_items: list) -> tuple:
    """Injects missing format indicators into the Output Requirements section."""
    if not missing_items:
        return text, []
        
    restored = []
    # For format indicators, we add a note rather than raw symbols
    injection = f"- [RESTORED FORMAT NOTE] Ensure output includes: {', '.join(missing_items)}\n"
    
    pattern = re.compile(r"(^Output Requirements:\s*\n?)", re.MULTILINE | re.IGNORECASE)
    if pattern.search(text):
        text = pattern.sub(rf"\1{injection}", text, count=1)
    else:
        text += f"\n\nOutput Requirements:\n{injection}"
        
    for item in missing_items:
        restored.append(f"Restored format indicator: {item}")
    return text, restored

def repair_prompt(prompt_ir: dict, optimized_prompt: str, eval_report: dict) -> tuple:
    """
    Main repair orchestrator.
    Checks evaluation report and applies repairs if thresholds are breached.
    """
    restored_items = []
    warnings = []
    
    # Thresholds
    CONSTRAINT_THRESHOLD = 1.0
    FEATURE_THRESHOLD = 0.8
    FORMAT_THRESHOLD = 0.9
    
    # 1. Check Constraints
    c_score = eval_report.get("constraint_score", {}).get("score", 1.0)
    c_missing = eval_report.get("constraint_score", {}).get("missing_items", [])
    if c_score < CONSTRAINT_THRESHOLD and c_missing:
        optimized_prompt, steps = repair_missing_constraints(optimized_prompt, c_missing)
        restored_items.extend(steps)
        warnings.append(f"Constraint preservation was {c_score*100:.0f}%. Restored {len(c_missing)} missing constraints.")

    # 2. Check Features
    f_score = eval_report.get("feature_score", {}).get("score", 1.0)
    f_missing = eval_report.get("feature_score", {}).get("missing_items", [])
    if f_score < FEATURE_THRESHOLD and f_missing:
        optimized_prompt, steps = repair_missing_features(optimized_prompt, f_missing)
        restored_items.extend(steps)
        warnings.append(f"Feature coverage was {f_score*100:.0f}%. Restored {len(f_missing)} missing features.")

    # 3. Check Output Format
    o_score = eval_report.get("format_score", {}).get("score", 1.0)
    o_missing = eval_report.get("format_score", {}).get("missing_items", [])
    if o_score < FORMAT_THRESHOLD and o_missing:
        optimized_prompt, steps = repair_missing_output_requirements(optimized_prompt, o_missing)
        restored_items.extend(steps)
        warnings.append(f"Output format score was {o_score*100:.0f}%. Restored {len(o_missing)} format indicators.")

    # Update Traceability
    if "traceability" not in prompt_ir:
        prompt_ir["traceability"] = {}
    prompt_ir["traceability"]["restored_items"] = restored_items
    prompt_ir["traceability"]["warnings"] = warnings
    
    return optimized_prompt, prompt_ir