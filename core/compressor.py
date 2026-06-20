import re

# Rule-based filler replacements
FILLER_REPLACEMENTS = {
    "please make sure that": "ensure",
    "make sure that": "ensure",
    "please ensure that": "ensure",
    "take that into consideration": "consider",
    "without missing any feature i mentioned": "preserve all mentioned features",
    "give me a detailed explanation of": "explain",
    "i want you to": "",
    "can you please": "",
    "it would be great if": "",
    "make sure to": "ensure",
    "it is important to": "",
    "in order to": "to"
}

def remove_duplicate_lines(lines):
    seen = set()
    result = []
    for line in lines:
        stripped = line.strip()
        # Case-insensitive duplicate check
        if stripped and stripped.lower() not in seen:
            seen.add(stripped.lower())
            result.append(line)
        elif not stripped:
            # Keep single blank lines for readability
            if not result or result[-1].strip():
                result.append(line)
    return result

def remove_duplicate_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    seen = set()
    result = []
    for sent in sentences:
        stripped = sent.strip().lower()
        if stripped and stripped not in seen:
            seen.add(stripped)
            result.append(sent)
    return " ".join(result)

def shorten_fillers(text):
    for filler, replacement in FILLER_REPLACEMENTS.items():
        pattern = re.compile(re.escape(filler), re.IGNORECASE)
        text = pattern.sub(replacement, text)
    # Clean up multiple spaces and trim
    text = re.sub(r' +', ' ', text).strip()
    text = re.sub(r'\n +', '\n', text)
    return text

def compress_section(text, strategy):
    if strategy == "preserve":
        return text, []
    if strategy == "remove":
        return "", ["Section removed entirely"]
    
    removed_items = []
    
    # 1. Shorten fillers
    original_text = text
    text = shorten_fillers(text)
    if text != original_text:
        removed_items.append("Shortened filler phrases")
        
    # 2. Remove duplicate lines
    lines = text.split('\n')
    unique_lines = remove_duplicate_lines(lines)
    if len(unique_lines) < len(lines):
        removed_items.append(f"Removed {len(lines) - len(unique_lines)} duplicate lines")
    text = '\n'.join(unique_lines)
    
    # 3. Moderate/Aggressive: Remove duplicate sentences
    if strategy in ["compress_moderate", "compress_aggressive"]:
        no_dup_sents = remove_duplicate_sentences(text)
        if len(no_dup_sents) < len(text):
            removed_items.append("Removed duplicate sentences")
        text = no_dup_sents
        
    return text, removed_items

def compress_prompt(prompt_ir):
    compressed_sections = {
        "task": "",
        "constraints": "",
        "features": "",
        "output_requirements": "",
        "context": ""
    }
    
    all_steps = []
    
    for section in prompt_ir["sections"]:
        name = section["name"].lower()
        content = section["content"]
        strategy = section.get("strategy", "preserve")
        
        compressed_text, steps = compress_section(content, strategy)
        
        for step in steps:
            all_steps.append(f"[{section['name']}] {step}")
            
        # Map to our 5 main reconstruction categories
        if name == "task":
            compressed_sections["task"] += compressed_text + "\n"
        elif name == "constraints":
            compressed_sections["constraints"] += compressed_text + "\n"
        elif name == "features":
            compressed_sections["features"] += compressed_text + "\n"
        elif name == "output_format":
            compressed_sections["output_requirements"] += compressed_text + "\n"
        else: # context, examples, other
            compressed_sections["context"] += compressed_text + "\n"
            
    # Clean up trailing newlines
    for key in compressed_sections:
        compressed_sections[key] = compressed_sections[key].strip()
        
    prompt_ir["traceability"]["compression_steps"] = all_steps
    
    return compressed_sections, prompt_ir