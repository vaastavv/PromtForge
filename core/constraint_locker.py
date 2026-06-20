def lock_constraints(prompt_ir):
    """
    Ensures all critical components are locked and adds warnings if constraints are missing.
    """
    warnings = prompt_ir["traceability"].get("warnings", [])
    
    # 1. Lock Task
    prompt_ir["task"]["locked"] = True
    
    # 2. Lock Output Requirements
    prompt_ir["output_requirements"]["locked"] = True
    
    # 3. Lock Constraints
    for c in prompt_ir["constraints"]:
        c["locked"] = True
        c["priority"] = "critical"
        c["compressibility"] = "very_low"
        
    # 4. Lock Required Features
    for f in prompt_ir["features"]:
        if f.get("required", False):
            f["locked"] = True
            f["compressibility"] = "low"
            
    # 5. Update Sections based on locks
    for section in prompt_ir["sections"]:
        name = section["name"].lower()
        if name in ["constraints", "output_format", "task"]:
            section["locked"] = True
            section["strategy"] = "preserve"
        elif name == "features":
            section["locked"] = True
            section["strategy"] = "compress_light"

    # 6. Check for missing constraints
    if not prompt_ir["constraints"]:
        warnings.append("WARNING: No explicit constraints detected. Prompt may be unsafe to compress aggressively.")
        
    prompt_ir["traceability"]["warnings"] = warnings
    return prompt_ir