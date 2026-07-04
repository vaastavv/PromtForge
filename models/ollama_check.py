"""
Ollama Status Checker
Safely detects if Ollama is installed, running, and lists available models.
"""
import shutil
import requests

OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_installed() -> bool:
    """Checks if the Ollama executable is in the system PATH."""
    return shutil.which("ollama") is not None

def check_ollama_running() -> bool:
    """Checks if the Ollama server is currently running and responding."""
    try:
        # Ping the tags endpoint with a short timeout to prevent app freezing
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def list_available_models() -> list:
    """Returns a list of locally downloaded Ollama models."""
    if not check_ollama_running():
        return []
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model.get("name", "") for model in data.get("models", [])]
    except Exception:
        pass
    return []

def get_ollama_status() -> dict:
    """Returns a comprehensive status dictionary for the UI."""
    installed = check_ollama_installed()
    running = check_ollama_running()
    models = list_available_models() if running else []

    if not installed:
        return {"status": "Not Installed", "message": "Ollama is not installed on this system.", "models": []}
    if not running:
        return {"status": "Not Running", "message": "Ollama is installed but the server is not running.", "models": []}
    
    return {"status": "Available", "message": "Ollama is running and ready.", "models": models}