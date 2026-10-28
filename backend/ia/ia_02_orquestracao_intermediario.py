import os
import requests

def executar_nivel_2(prompt: str, contexto: str = "") -> dict:
    """Nível 2: RAG, sintetizador e organizador de tarefas intermediárias."""
    ollama_url = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    system_prompt = (
        "Você é o Agente Nível 2 (Orquestrador/RAG) do Cockpit SP-Águas. "
        "Especialista em organização de dados, síntese de relatórios e conciliação de informações."
    )
    payload = {
        "model": "agente-geral:latest",
        "prompt": f"{system_prompt}\n\nContexto: {contexto}\n\nDemanda: {prompt}",
        "stream": False,
        "options": {"temperature": 0.30, "num_ctx": 8192}
    }
    resp = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=8)
    resp.raise_for_status()
    return {"resposta": resp.json().get("response", ""), "modelo": "agente-geral:latest", "nivel": 2}