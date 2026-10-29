import os
import requests

def executar_nivel_3(prompt: str, contexto: str = "") -> dict:
    """NÃ­vel 3: Tarefas atÃ´micas, classificaÃ§Ã£o rÃ¡pida e logs (~0.4 GB RAM)."""
    ollama_url = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": f"ClassificaÃ§Ã£o rÃ¡pida e direta SP-Ãguas:\nContexto: {contexto}\nDemanda: {prompt}",
        "stream": False,
        "options": {"temperature": 0.20, "num_ctx": 4096}
    }
    resp = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=25)
    resp.raise_for_status()
    return {"resposta": resp.json().get("response", ""), "modelo": "qwen2.5-coder:3b", "nivel": 3}