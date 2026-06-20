def reconstruct_prompt(compressed_sections):
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