"""
Rule-Based Compressor
Executes the compression plan assigned by the planner.
"""
import re

# Rule-based filler replacements
FILLER_REPLACEMENTS = {
    "please make sure that": "ensure", "make sure that": "ensure",
    "take that into consideration": "consider",
    "without missing any feature i mentioned": "preserve all mentioned features",
    "give me a detailed explanation of": "explain",
    "i want you to": "", "can you please": "", "it would be great if": "",
    "make sure to": "ensure", "it is important to": "", "in order to": "to"
}

def remove_duplicate_lines(lines):
    seen = set()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped.lower() not in seen:
            seen.add(stripped.lower())
            result.append(line)
        elif not stripped:
            if not result or result[-1].strip():
                result.append(line)
    return result

def shorten_fillers(text):
    for filler, replacement in FILLER_REPLACEMENTS.items():
        text = re.sub(re.escape(filler), replacement, text, flags=re.IGNORECASE)
    return re.sub(r' +', ' ', text).strip()

def compress_section(text: str, action: str, relevance: float) -> tuple:
    """Compresses text based on the assigned action."""
    steps = []
    
    if action == "preserve":
        return text, ["Preserved (Locked/Critical)"]
        
    if action == "remove_if_low_value":
        if relevance < 0.4:
            return "", ["Removed (Low relevance/value)"]
        else:
            action = "compress_lightly" # Fallback if relevance isn't actually low
            
    if action in ["remove_duplicates", "compress_lightly", "summarize", "compress_aggressively"]:
        # 1. Shorten fillers (All actions except preserve)
        original = text
        text = shorten_fillers(text)
        if text != original:
            steps.append("Shortened filler phrases")
            
        # 2. Remove duplicate lines
        lines = text.split('\n')
        unique_lines = remove_duplicate_lines(lines)
        if len(unique_lines) < len(lines):
            steps.append(f"Removed {len(lines) - len(unique_lines)} duplicate lines")
        text = '\n'.join(unique_lines)
        
        # 3. Aggressive/Summarize specific logic
        if action == "compress_aggressively":
            # Remove duplicate sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            seen_sents = set()
            unique_sents = []
            for s in sentences:
                if s.lower().strip() not in seen_sents:
                    seen_sents.add(s.lower().strip())
                    unique_sents.append(s)
            if len(unique_sents) < len(sentences):
                steps.append("Removed duplicate sentences (Aggressive)")
            text = " ".join(unique_sents)
            
        elif action == "summarize":
            # Rule-based "summarize": Keep only the first sentence of each paragraph block
            paragraphs = text.split('\n\n')
            summarized = []
            for p in paragraphs:
                sents = re.split(r'(?<=[.!?])\s+', p.strip())
                if sents:
                    summarized.append(sents[0]) # Keep first sentence
            if summarized:
                text = " ".join(summarized)
                steps.append("Summarized (Kept first sentence of blocks)")

    return text, steps

def compress_prompt(prompt_ir: dict) -> tuple:
    """Main compressor loop. Maps sections to output buckets."""
    compressed_sections = {
        "task": "", "constraints": "", "features": "", 
        "output_requirements": "", "context": ""
    }
    all_steps = []
    
    for section in prompt_ir.get("sections", []):
        name = section.get("name", "other").lower()
        content = section.get("content", "")
        action = section.get("compression_action", "compress_lightly")
        relevance = section.get("relevance_score", 0.5)
        
        compressed_text, steps = compress_section(content, action, relevance)
        
        for step in steps:
            all_steps.append(f"[{section['name']}] {step}")
            
        # Map to reconstruction buckets
        if name == "task": compressed_sections["task"] += compressed_text + "\n"
        elif name == "constraints": compressed_sections["constraints"] += compressed_text + "\n"
        elif name == "features": compressed_sections["features"] += compressed_text + "\n"
        elif name == "output_format": compressed_sections["output_requirements"] += compressed_text + "\n"
        else: compressed_sections["context"] += compressed_text + "\n"
        
    for key in compressed_sections:
        compressed_sections[key] = compressed_sections[key].strip()
        
    prompt_ir["traceability"]["compression_steps"] = all_steps
    return compressed_sections, prompt_ir