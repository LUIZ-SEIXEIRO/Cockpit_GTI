import os
import requests

def executar_nivel_2(prompt: str, contexto: str = "") -> dict:
    """NÃ­vel 2: RAG, sintetizador e organizador de tarefas intermediÃ¡rias."""
    ollama_url = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    system_prompt = (
        "VocÃª Ã© o Agente NÃ­vel 2 (Orquestrador/RAG) do Cockpit SP-Ãguas. "
        "Especialista em organizaÃ§Ã£o de dados, sÃ­ntese de relatÃ³rios e conciliaÃ§Ã£o de informaÃ§Ãµes."
    )
    payload = {
        "model": "agente-geral:latest",
        "prompt": f"{system_prompt}\n\nContexto: {contexto}\n\nDemanda: {prompt}",
        "stream": False,
        "options": {"temperature": 0.30, "num_ctx": 8192}
    }
    resp = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=40)
    resp.raise_for_status()
    return {"resposta": resp.json().get("response", ""), "modelo": "agente-geral:latest", "nivel": 2}