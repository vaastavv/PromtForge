import re
from typing import List, Dict, Any

def preprocess_prompt(raw_text: str) -> Dict[str, Any]:
    """
    Main preprocessor function. Cleans, normalizes, and chunks the raw prompt.
    """
    if not raw_text or not raw_text.strip():
        return _empty_result()

    # 1. Normalize line endings (Windows \r\n -> \n, Mac \r -> \n)
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Remove trailing spaces from each line
    lines = text.split("\n")
    lines = [line.rstrip() for line in lines]

    # 3. Collapse multiple blank lines into one blank line
    text = "\n".join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 4. Split text into final clean lines
    clean_lines = text.split("\n")

    # 5. Split text into chunks (paragraph/size based)
    chunks = _split_into_chunks(clean_lines, max_chunk_chars=1000)

    # 6. Calculate stats
    stats = _calculate_stats(raw_text, text, clean_lines, chunks)

    return {
        "raw_text": raw_text,
        "clean_text": text,
        "lines": clean_lines,
        "chunks": chunks,
        "stats": stats
    }

def _split_into_chunks(lines: List[str], max_chunk_chars: int = 1000) -> List[str]:
    """
    Groups lines into chunks. If a single line exceeds max_chunk_chars, 
    it gets its own chunk to prevent breaking code blocks.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        # +1 accounts for the newline character when joined
        line_length = len(line) + 1 
        
        # If adding this line exceeds the limit and we already have content, start a new chunk
        if current_length + line_length > max_chunk_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    # Add the final chunk
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

def _calculate_stats(raw_text: str, clean_text: str, lines: List[str], chunks: List[str]) -> Dict[str, int]:
    """
    Calculates preprocessing statistics.
    """
    # Approximate word count based on clean text
    word_count = len(clean_text.split())

    return {
        "char_count_before": len(raw_text),
        "char_count_after": len(clean_text),
        "line_count": len(lines),
        "chunk_count": len(chunks),
        "approx_word_count": word_count
    }

def _empty_result() -> Dict[str, Any]:
    """Returns an empty dictionary structure if input is empty."""
    return {
        "raw_text": "",
        "clean_text": "",
        "lines": [],
        "chunks": [],
        "stats": {
            "char_count_before": 0,
            "char_count_after": 0,
            "line_count": 0,
            "chunk_count": 0,
            "approx_word_count": 0
        }
    }