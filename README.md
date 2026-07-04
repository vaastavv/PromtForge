## 🦙 Optional: Local LLM Polish (Ollama)

PromptForge is designed to work perfectly **without** any LLM. However, in Phase 3, we introduce an optional "Local LLM Polish" step that uses Ollama to rewrite the compressed prompt for better flow and readability.

### Why is it optional?
- **Privacy:** Everything runs 100% locally on your machine. No data is sent to the cloud.
- **Hardware Constraints:** Not everyone has a powerful GPU. The core rule-based compiler works on any 8GB RAM laptop.
- **Zero Cost:** Ollama is completely free and uses no paid APIs.

### How to Install Ollama
1. Download the Windows installer from [https://ollama.com](https://ollama.com).
2. Run the installer. Ollama will start automatically in your system tray.

### Recommended Models for 8GB RAM
If you want to test the LLM polish feature, you **must** use small models. Large models will freeze your computer.

Run these commands in your terminal to download a safe model:
```powershell
# Highly Recommended (Fastest, ~1.3GB)
ollama pull llama3.2:1b

# Alternative (Slightly smarter, ~2.3GB)
ollama pull phi3:mini