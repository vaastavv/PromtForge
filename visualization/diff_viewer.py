"""
Diff Viewer for PromptForge
Compares original and optimized prompts to show what changed.
"""
from typing import List, Dict, Tuple


def compute_line_diff(original_text: str, optimized_text: str) -> Dict[str, List[str]]:
    """
    Compares original and optimized text line-by-line.
    Returns categorized lines: preserved, removed, added.
    """
    original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]
    optimized_lines = [line.strip() for line in optimized_text.split('\n') if line.strip()]
    
    preserved = []
    removed = []
    added = []
    
    # Track which optimized lines we've matched
    used_optimized = set()
    
    # Find preserved and removed lines
    for orig_line in original_lines:
        found = False
        for idx, opt_line in enumerate(optimized_lines):
            if idx not in used_optimized and _lines_match(orig_line, opt_line):
                preserved.append(orig_line)
                used_optimized.add(idx)
                found = True
                break
        if not found:
            removed.append(orig_line)
    
    # Find added lines (in optimized but not in original)
    for idx, opt_line in enumerate(optimized_lines):
        if idx not in used_optimized:
            added.append(opt_line)
    
    return {
        "preserved": preserved,
        "removed": removed,
        "added": added
    }


def _lines_match(line1: str, line2: str) -> bool:
    """Checks if two lines are similar enough to be considered preserved."""
    # Exact match
    if line1.lower() == line2.lower():
        return True
    
    # Check if one contains the other (for shortened lines)
    if line1.lower() in line2.lower() or line2.lower() in line1.lower():
        # But only if they share at least 60% of words
        words1 = set(line1.lower().split())
        words2 = set(line2.lower().split())
        if not words1 or not words2:
            return False
        overlap = len(words1.intersection(words2))
        similarity = overlap / max(len(words1), len(words2))
        return similarity >= 0.6
    
    return False


def calculate_diff_stats(diff_result: Dict[str, List[str]]) -> Dict[str, int]:
    """Calculate statistics from the diff result."""
    total_original = len(diff_result["preserved"]) + len(diff_result["removed"])
    total_optimized = len(diff_result["preserved"]) + len(diff_result["added"])
    
    return {
        "original_lines": total_original,
        "optimized_lines": total_optimized,
        "preserved_lines": len(diff_result["preserved"]),
        "removed_lines": len(diff_result["removed"]),
        "added_lines": len(diff_result["added"]),
        "preservation_rate": round(len(diff_result["preserved"]) / max(total_original, 1), 4)
    }