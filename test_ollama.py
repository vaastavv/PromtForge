"""
Standalone test script for the Ollama client.
Run this in your terminal: python test_ollama.py
"""
from models.ollama_client import is_ollama_available, get_available_models, rewrite_prompt_with_ollama

print("1. Checking if Ollama is available...")
available = is_ollama_available()
print(f"   Available: {available}")

if available:
    print("\n2. Fetching available models...")
    models = get_available_models()
    print(f"   Models: {models}")
    
    if models:
        print(f"\n3. Testing rewrite with model: {models[0]}")
        
        # Create a dummy Prompt IR and optimized prompt
        dummy_ir = {
            "task": {"text": "Write a python script to scrape data"},
            "constraints": [{"text": "No paid APIs", "locked": True}, {"text": "8GB RAM limit", "locked": True}],
            "features": [{"name": "Logging module", "locked": True}],
            "output_requirements": {"format": "json"}
        }
        dummy_prompt = "Write a python script to scrape data. No paid APIs. 8GB RAM limit. Logging module. JSON."
        
        result = rewrite_prompt_with_ollama(dummy_prompt, dummy_ir, models[0])
        
        if result["success"]:
            print("   ✅ Success! Rewritten prompt:")
            print("   " + result["rewritten_prompt"][:200] + "...")
        else:
            print(f"   ❌ Failed: {result['error']}")
    else:
        print("   ⚠️ No models found. Run 'ollama pull llama3.2:1b' first.")
else:
    print("   ❌ Ollama is not running. Please start the Ollama app.")