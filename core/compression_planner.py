def plan_compression(prompt_ir):
    """
    Assigns a compression strategy to each section based on the selected mode.
    """
    mode = prompt_ir["compression_policy"]["mode"]
    
    # Define strategies for non-locked sections based on mode
    mode_strategies = {
        "safe": {"context": "compress_light", "examples": "compress_light", "other": "preserve"},
        "balanced": {"context": "compress_moderate", "examples": "compress_aggressive", "other": "compress_light"},
        "aggressive": {"context": "compress_aggressive", "examples": "remove", "other": "remove"},
        "research": {"context": "compress_moderate", "examples": "compress_moderate", "other": "compress_light"}
    }
    
    strategies = mode_strategies.get(mode, mode_strategies["balanced"])
    
    for section in prompt_ir["sections"]:
        # If already locked by constraint_locker, respect that
        if section["locked"]:
            if section["name"].lower() in ["constraints", "output_format", "task"]:
                section["strategy"] = "preserve"
            elif section["name"].lower() == "features":
                section["strategy"] = "compress_light"
        else:
            name_lower = section["name"].lower()
            if name_lower in strategies:
                section["strategy"] = strategies[name_lower]
            else:
                section["strategy"] = "compress_light"
                
    return prompt_ir
