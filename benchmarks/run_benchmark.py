"""
PromptForge Benchmark Runner
Compares 4 compression methods across all benchmark prompts.
"""
import json
import time
import os
import sys

# Ensure parent directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.preprocessor import preprocess_prompt
from core.parser import parse_sections
from core.ir_generator import generate_prompt_ir
from core.constraint_locker import lock_constraints
from core.compression_planner import plan_compression
from core.compressor import compress_prompt, shorten_fillers, remove_duplicate_lines
from core.reconstructor import reconstruct_prompt
from benchmarks.evaluator import evaluate, estimate_tokens


# ==============================================================================
# Compression Methods
# ==============================================================================

def method_none(prompt_text: str, **kwargs) -> str:
    """Baseline: No compression. Returns original text."""
    return prompt_text


def method_truncation(prompt_text: str, target_reduction: float = 0.4, **kwargs) -> str:
    """Baseline: Naive truncation to target word count."""
    words = prompt_text.split()
    target_words = max(int(len(words) * (1 - target_reduction)), 10)
    return " ".join(words[:target_words])


def method_rule_based(prompt_text: str, **kwargs) -> str:
    """Baseline: Apply filler removal and dedup without IR pipeline."""
    text = shorten_fillers(prompt_text)
    lines = text.split('\n')
    lines = remove_duplicate_lines(lines)
    return '\n'.join(lines)


def method_promptforge(prompt_text: str, mode: str = "Balanced", **kwargs) -> str:
    """Full PromptForge pipeline."""
    preprocessed = preprocess_prompt(prompt_text)
    parsed = parse_sections(preprocessed)
    ir = generate_prompt_ir(preprocessed, parsed, mode)
    ir = lock_constraints(ir)
    ir = plan_compression(ir)
    compressed_sections, ir = compress_prompt(ir)
    return reconstruct_prompt(compressed_sections)


# Dictionary of methods
METHODS = {
    "none": method_none,
    "truncation": method_truncation,
    "rule_based": method_rule_based,
    "promptforge": method_promptforge
}


# ==============================================================================
# Benchmark Runner Function
# ==============================================================================

def run_benchmark(prompts_file=None, output_file=None, mode="Balanced", progress_callback=None):
    """
    Runs all methods on all benchmark prompts and returns results.
    """
    if prompts_file is None:
        prompts_file = os.path.join(os.path.dirname(__file__), "sample_prompts.json")
    if output_file is None:
        output_file = os.path.join(os.path.dirname(__file__), "results.csv")

    # Load prompts
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    results = []
    total_steps = len(prompts) * len(METHODS)
    current_step = 0

    # Run benchmarks
    for prompt_data in prompts:
        prompt_text = prompt_data["prompt"]

        for method_name, method_func in METHODS.items():
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps,
                                  f"Testing {method_name} on {prompt_data['id']}...")

            try:
                start_time = time.time()

                if method_name == "promptforge":
                    compressed = method_func(prompt_text, mode=mode)
                else:
                    compressed = method_func(prompt_text)

                latency = round(time.time() - start_time, 4)

                # Evaluate
                scores = evaluate(prompt_text, compressed, prompt_data)

                results.append({
                    "prompt_id": prompt_data["id"],
                    "category": prompt_data["category"],
                    "method": method_name,
                    "original_tokens": scores["original_tokens"],
                    "compressed_tokens": scores["compressed_tokens"],
                    "token_reduction": scores["token_reduction"],
                    "constraint_preservation": scores["constraint_preservation"],
                    "feature_coverage": scores["feature_coverage"],
                    "output_format_score": scores["output_format_score"],
                    "keyword_preservation": scores["keyword_preservation"],
                    "risk": scores["risk"],
                    "final_score": scores["final_score"],
                    "latency_seconds": latency
                })

            except Exception as e:
                results.append({
                    "prompt_id": prompt_data["id"],
                    "category": prompt_data["category"],
                    "method": method_name,
                    "error": str(e),
                    "token_reduction": 0,
                    "constraint_preservation": 0,
                    "feature_coverage": 0,
                    "output_format_score": 0,
                    "keyword_preservation": 0,
                    "final_score": 0,
                    "latency_seconds": 0
                })

    # Save to CSV
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
    except ImportError:
        import csv
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if results:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

    return results


# ==============================================================================
# Main entry point
# ==============================================================================

if __name__ == "__main__":
    print("Running PromptForge Benchmark Suite...")
    results = run_benchmark()
    print(f"\nBenchmark complete! {len(results)} results saved.")

    try:
        import pandas as pd
        df = pd.DataFrame(results)
        print("\n=== Method Comparison (Averages) ===")
        summary = df.groupby("method")[
            ["token_reduction", "constraint_preservation", "feature_coverage",
             "keyword_preservation", "final_score"]
        ].mean().round(4)
        print(summary.to_string())
    except ImportError:
        print("Install pandas for summary tables: pip install pandas")