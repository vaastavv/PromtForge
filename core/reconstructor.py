"""
Prompt Reconstructor with Adaptive Repair and Mode-Aware Formatting
Builds the final optimized prompt from Prompt IR sections.
"""
from typing import Dict, List, Tuple

def reconstruct_prompt(compressed_sections: Dict[str, str], prompt_ir: Dict) -> Tuple[str, Dict]:
    """
    Reconstructs the final optimized prompt from compressed sections.
    Applies mode-specific formatting and deduplication.
    """
    mode = prompt_ir.get("compression_policy", {}).get("mode", "balanced")
    parts = []
    trace_steps = []

    # Helper to deduplicate lines while preserving order
    def deduplicate(text: str) -> List[str]:
        lines = text.split('\n')
        seen = set()
        unique = []
        for line in lines:
            clean = line.strip().lower()
            if clean and clean not in seen:
                seen.add(clean)
                unique.append(line.strip())
        return unique

    # Helper to format lists based on mode
    def format_list(items: List[str], mode: str) -> str:
        if not items:
            return ""
        if mode == "aggressive":
            # Very compact: inline comma-separated
            return ", ".join(items)
        elif mode == "research":
            # Structured: numbered list for traceability
            return "\n".join([f"[{i+1}] {item}" for i, item in enumerate(items)])
        else: 
            # Safe/Balanced: standard bullet points
            return "\n".join([f"- {item}" for item in items])

    # 1. Task
    if compressed_sections.get("task"):
        task_lines = deduplicate(compressed_sections["task"])
        task_text = " ".join(task_lines) if mode == "aggressive" else "\n".join(task_lines)
        parts.append(f"Task:\n{task_text}")
        trace_steps.append("Reconstructed Task section.")

    # 2. Constraints
    if compressed_sections.get("constraints"):
        c_lines = deduplicate(compressed_sections["constraints"])
        parts.append(f"Constraints:\n{format_list(c_lines, mode)}")
        trace_steps.append("Reconstructed Constraints section.")

    # 3. Features
    if compressed_sections.get("features"):
        f_lines = deduplicate(compressed_sections["features"])
        parts.append(f"Required Features:\n{format_list(f_lines, mode)}")
        trace_steps.append("Reconstructed Features section.")

    # 4. Output Requirements
    if compressed_sections.get("output_requirements"):
        o_lines = deduplicate(compressed_sections["output_requirements"])
        o_text = " ".join(o_lines) if mode == "aggressive" else "\n".join(o_lines)
        parts.append(f"Output Requirements:\n{o_text}")
        trace_steps.append("Reconstructed Output Requirements section.")

    # 5. Context
    if compressed_sections.get("context"):
        ctx_lines = deduplicate(compressed_sections["context"])
        ctx_text = " ".join(ctx_lines) if mode == "aggressive" else "\n".join(ctx_lines)
        parts.append(f"Additional Context:\n{ctx_text}")
        trace_steps.append("Reconstructed Context section.")

    # Join all parts
    final_prompt = "\n\n".join(parts)
    
    # Update traceability
    if "traceability" not in prompt_ir:
        prompt_ir["traceability"] = {}
    if "reconstruction_steps" not in prompt_ir["traceability"]:
        prompt_ir["traceability"]["reconstruction_steps"] = []
        
    prompt_ir["traceability"]["reconstruction_steps"].extend(trace_steps)
    prompt_ir["traceability"]["reconstruction_steps"].append("Reconstructed optimized prompt from Prompt IR.")

    return final_prompt, prompt_ir


def adaptive_repair(
    optimized_prompt: str,
    prompt_ir: Dict,
    repair_missing_constraints: bool = True,
    repair_missing_features: bool = True,
    repair_missing_format: bool = True
) -> tuple:
    """
    Checks if critical elements are missing from the optimized prompt and repairs them.
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