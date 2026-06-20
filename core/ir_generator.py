import uuid
from datetime import datetime
from typing import Dict, Any, List

def generate_prompt_ir(preprocessed_data: Dict[str, Any], parsed_data: Dict[str, Any], compression_mode: str) -> Dict[str, Any]:
    """
    Generates the Prompt Intermediate Representation (IR) from preprocessed and parsed data.
    """
    # 1. Metadata
    metadata = {
        "prompt_id": str(uuid.uuid4())[:8],
        "created_at": datetime.now().isoformat(),
        "language": "en",
        "domain": _infer_domain(parsed_data),
        "version": "1.0"
    }

    # 2. Intent & Task
    task_items = parsed_data.get("task", [])
    task_text = " ".join([item["text"] for item in task_items]) if task_items else "No explicit task detected."
    
    intent = {
        "primary_goal": task_text[:100] + "..." if len(task_text) > 100 else task_text,
        "task_type": _infer_task_type(task_text),
        "success_criteria": [item["text"] for item in parsed_data.get("output_format", [])]
    }

    task = {
        "text": task_text,
        "priority": "critical",
        "locked": True
    }

    # 3. Constraints
    constraints = []
    for i, item in enumerate(parsed_data.get("constraints", [])):
        text = item["text"]
        constraints.append({
            "id": f"C{i+1:03d}",
            "text": text,
            "normalized_text": text.lower().strip(),
            "type": _classify_constraint(text),
            "priority": "critical",
            "locked": True,
            "compressibility": "very_low"
        })

    # 4. Features
    features = []
    for i, item in enumerate(parsed_data.get("features", [])):
        text = item["text"]
        # Clean up the feature name (remove bullet points, etc.)
        name = text.lstrip("-•* ").strip()
        features.append({
            "id": f"F{i+1:03d}",
            "name": name if name else text,
            "required": True,
            "priority": "high",
            "locked": False,
            "compressibility": "low"
        })

    # 5. Output Requirements
    output_format_items = parsed_data.get("output_format", [])
    output_req = {
        "format": _detect_output_format(output_format_items),
        "structure": [item["text"] for item in output_format_items],
        "must_include": [],
        "locked": True
    }

    # 6. Sections
    sections = []
    section_idx = 1
    for category, items in parsed_data.items():
        if items:
            for item in items:
                sections.append({
                    "id": f"S{section_idx:03d}",
                    "name": category.capitalize(),
                    "content": item["text"],
                    "importance": "high" if category in ["constraints", "task", "output_format"] else "medium",
                    "strategy": "preserve" if category in ["constraints", "output_format"] else "compress",
                    "locked": category in ["constraints", "output_format"]
                })
                section_idx += 1

    # 7. Compression Policy
    compression_policy = _get_compression_policy(compression_mode)

    # 8. Evaluation Targets
    evaluation_targets = {
        "minimum_constraint_score": 1.0,
        "minimum_feature_coverage": 0.9,
        "minimum_semantic_similarity": 0.85,
        "minimum_output_format_score": 0.9,
        "target_token_reduction": compression_policy["target_reduction"]
    }

    # 9. Traceability
    traceability = {
        "source_lines": {f"L{i}": line for i, line in enumerate(preprocessed_data.get("lines", []))},
        "compression_steps": [],
        "restored_items": [],
        "warnings": []
    }

    return {
        "metadata": metadata,
        "intent": intent,
        "task": task,
        "constraints": constraints,
        "features": features,
        "output_requirements": output_req,
        "sections": sections,
        "compression_policy": compression_policy,
        "evaluation_targets": evaluation_targets,
        "traceability": traceability
    }

def _classify_constraint(text: str) -> str:
    """Rule-based classifier to determine the specific type of constraint."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["8gb", "ram", "memory", "resource", "hardware"]):
        return "hardware_constraint"
    if any(w in text_lower for w in ["api", "paid", "free", "cost", "price", "money"]):
        return "cost_constraint"
    if any(w in text_lower for w in ["json", "format", "table", "markdown", "output", "strictly"]):
        return "format_constraint"
    if any(w in text_lower for w in ["offline", "local", "cloud", "deploy", "internet"]):
        return "deployment_constraint"
    if any(w in text_lower for w in ["tool", "python", "library", "ollama", "software"]):
        return "tool_constraint"
    if any(w in text_lower for w in ["miss", "preserve", "include", "feature", "all"]):
        return "coverage_constraint"
    if any(w in text_lower for w in ["quality", "expert", "best", "accurate", "professional"]):
        return "quality_constraint"
    return "general_constraint"

def _infer_domain(parsed_data: Dict[str, Any]) -> str:
    """Simple heuristic to guess the domain of the prompt."""
    all_text = " ".join([item["text"] for cat in parsed_data.values() for item in cat]).lower()
    if any(w in all_text for w in ["python", "code", "script", "developer", "api"]):
        return "software_engineering"
    if any(w in all_text for w in ["data", "analysis", "chart", "graph"]):
        return "data_science"
    return "general"

def _infer_task_type(task_text: str) -> str:
    """Infers the primary task type from the task text."""
    text_lower = task_text.lower()
    if any(w in text_lower for w in ["write", "code", "script", "build", "develop"]):
        return "code_generation"
    if any(w in text_lower for w in ["explain", "describe", "analyze"]):
        return "explanation"
    if any(w in text_lower for w in ["summarize", "compress", "shorten"]):
        return "summarization"
    return "general_instruction"

def _detect_output_format(items: List[Dict[str, Any]]) -> str:
    """Detects the requested output format from the output_format parsed items."""
    all_text = " ".join([item["text"] for item in items]).lower()
    if "json" in all_text: return "json"
    if "markdown" in all_text: return "markdown"
    if "table" in all_text: return "table"
    if "code" in all_text or "script" in all_text: return "code_block"
    return "plain_text"

def _get_compression_policy(mode: str) -> Dict[str, Any]:
    """Returns the compression policy dictionary based on the selected UI mode."""
    policies = {
        "Safe": {"mode": "safe", "target_reduction": 0.1, "preserve_constraints": True, "preserve_required_features": True, "preserve_output_format": True, "repair_if_missing": True},
        "Balanced": {"mode": "balanced", "target_reduction": 0.4, "preserve_constraints": True, "preserve_required_features": True, "preserve_output_format": True, "repair_if_missing": True},
        "Aggressive": {"mode": "aggressive", "target_reduction": 0.7, "preserve_constraints": True, "preserve_required_features": True, "preserve_output_format": True, "repair_if_missing": True},
        "Research": {"mode": "research", "target_reduction": 0.3, "preserve_constraints": True, "preserve_required_features": True, "preserve_output_format": True, "repair_if_missing": True}
    }
    return policies.get(mode, policies["Balanced"])