"""
Ollama Client for Local LLM Rewriting
Handles communication with the local Ollama API safely.
"""
import requests

OLLAMA_BASE_URL = "http://localhost:11434"

def is_ollama_available() -> bool:
    """Checks if the Ollama server is running."""
    try:
        # Ping the tags endpoint with a short timeout to prevent app freezing
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_available_models() -> list:
    """Returns a list of available models in Ollama."""
    if not is_ollama_available():
        return []
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model.get("name") for model in data.get("models", [])]
    except Exception:
        pass
    return []

def call_ollama(prompt: str, model_name: str) -> dict:
    """
    Calls the Ollama /api/generate endpoint.
    Returns a dict with 'success' (bool), 'response' (str), and 'error' (str).
    """
    if not is_ollama_available():
        return {"success": False, "response": "", "error": "Ollama is not running."}
        
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,  # Low temperature for strict adherence
            "num_predict": 2048
        }
    }
    
    try:
        # Timeout set to 120 seconds to allow for slow local generation on 8GB RAM
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            return {"success": True, "response": data.get("response", ""), "error": ""}
        else:
            return {"success": False, "response": "", "error": f"Ollama returned status {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "response": "", "error": "Ollama took too long to respond (Timeout)."}
    except Exception as e:
        return {"success": False, "response": "", "error": str(e)}

def rewrite_prompt_with_ollama(optimized_prompt: str, prompt_ir: dict, model_name: str) -> dict:
    """
    Rewrites the optimized prompt using Ollama, ensuring locked items are preserved.
    Returns a dict with 'success', 'rewritten_prompt', and 'error'.
    """
    if not is_ollama_available():
        return {"success": False, "rewritten_prompt": "", "error": "Ollama is not running."}
        
    # Extract locked items from IR to enforce preservation
    locked_constraints = [c["text"] for c in prompt_ir.get("constraints", []) if c.get("locked")]
    locked_features = [f["name"] for f in prompt_ir.get("features", []) if f.get("locked")]
    task_text = prompt_ir.get("task", {}).get("text", "")
    output_format = prompt_ir.get("output_requirements", {}).get("format", "")
    
    context = ""
    if locked_constraints:
        context += f"\nLocked Constraints (MUST KEEP):\n" + "\n".join([f"- {c}" for c in locked_constraints])
    if locked_features:
        context += f"\nLocked Features (MUST KEEP):\n" + "\n".join([f"- {f}" for f in locked_features])
    if task_text:
        context += f"\nTask (MUST KEEP):\n{task_text}"
    if output_format:
        context += f"\nOutput Format (MUST KEEP):\n{output_format}"

    system_instruction = (
        "You are an expert prompt engineer. Rewrite the following optimized prompt to be concise and clear.\n"
        "Preserve all locked constraints, required features, task, and output requirements exactly.\n"
        "Do not remove any must-keep instruction.\n"
        "Do not add paid API requirements.\n"
        "Return only the rewritten prompt.\n\n"
        f"{context}\n\n"
        f"[PROMPT TO REWRITE]:\n{optimized_prompt}"
    )
    
    result = call_ollama(system_instruction, model_name)
    
    if result["success"]:
        # Clean up the response (remove any markdown code blocks if the LLM added them)
        rewritten = result["response"].strip()
        if rewritten.startswith("```"):
            rewritten = rewritten.split("\n", 1)[1] if "\n" in rewritten else rewritten[3:]
        if rewritten.endswith("```"):
            rewritten = rewritten[:-3]
            
        return {"success": True, "rewritten_prompt": rewritten.strip(), "error": ""}
    else:
        return {"success": False, "rewritten_prompt": "", "error": result["error"]}