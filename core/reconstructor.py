"""
Prompt Reconstructor with Adaptive Repair
Builds the final optimized prompt and repairs missing elements.
"""
from typing import Dict, List


def reconstruct_prompt(compressed_sections: Dict[str, str]) -> str:
    """
    Reconstructs the final optimized prompt from compressed sections.
    """
    parts = []
    
    if compressed_sections.get("task"):
        parts.append("Task:\n" + compressed_sections["task"])
        
    if compressed_sections.get("constraints"):
        parts.append("Constraints:\n" + compressed_sections["constraints"])
        
    if compressed_sections.get("features"):
        parts.append("Required Features:\n" + compressed_sections["features"])
        
    if compressed_sections.get("output_requirements"):
        parts.append("Output Requirements:\n" + compressed_sections["output_requirements"])
        
    if compressed_sections.get("context"):
        parts.append("Additional Context:\n" + compressed_sections["context"])
        
    return "\n\n".join(parts)


def adaptive_repair(
    optimized_prompt: str,
    prompt_ir: Dict,
    repair_missing_constraints: bool = True,
    repair_missing_features: bool = True,
    repair_missing_format: bool = True
) -> tuple:
    """
    Checks if critical elements are missing from the optimized prompt and repairs them.
    
    Returns:
        - repaired_prompt: The fixed prompt
        - repair_log: List of repairs made
        - warnings: List of warnings about missing items that couldn't be repaired
    """
    repair_log = []
    warnings = []
    
    optimized_lower = optimized_prompt.lower()
    repairs_needed = []
    
    # Check constraints
    if repair_missing_constraints:
        for constraint in prompt_ir.get("constraints", []):
            text = constraint.get("text", "")
            words = text.lower().split()
            if not words:
                continue
            
            # Check if constraint is preserved (60% word match)
            match_count = sum(1 for w in words if w in optimized_lower)
            if match_count < max(len(words) * 0.6, 1):
                repairs_needed.append(("constraint", text))
    
    # Check features
    if repair_missing_features:
        for feature in prompt_ir.get("features", []):
            name = feature.get("name", "")
            words = name.lower().split()
            if not words:
                continue
            
            match_count = sum(1 for w in words if w in optimized_lower)
            if match_count < max(len(words) * 0.5, 1):
                repairs_needed.append(("feature", name))
    
    # Check output format
    if repair_missing_format:
        output_req = prompt_ir.get("output_requirements", {})
        if output_req.get("locked"):
            format_str = output_req.get("format", "")
            if format_str and format_str.lower() not in optimized_lower:
                repairs_needed.append(("format", f"Output must be in {format_str} format"))
    
    # Apply repairs
    if repairs_needed:
        repaired_prompt = optimized_prompt + "\n\n---\n**Critical Requirements (Restored):**\n"
        
        for item_type, item_text in repairs_needed:
            if item_type == "constraint":
                repaired_prompt += f"- [CONSTRAINT] {item_text}\n"
                repair_log.append(f"Restored missing constraint: {item_text}")
            elif item_type == "feature":
                repaired_prompt += f"- [FEATURE] {item_text}\n"
                repair_log.append(f"Restored missing feature: {item_text}")
            elif item_type == "format":
                repaired_prompt += f"- [FORMAT] {item_text}\n"
                repair_log.append(f"Restored missing format requirement: {item_text}")
        
        return repaired_prompt, repair_log, warnings
    
    return optimized_prompt, repair_log, warnings