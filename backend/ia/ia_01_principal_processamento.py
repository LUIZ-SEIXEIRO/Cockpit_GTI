import os
import requests

def executar_nivel_1(prompt: str, contexto: str = "") -> dict:
    """Nível 1: Análise profunda (ETP, TR, Pareceres, Conformidade)."""
    ollama_url = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    system_prompt = (
        "Você é o Agente Nível 1 (Alto Desempenho) do Cockpit SP-Águas. "
        "Especialista em contratações públicas de TIC (Lei 14.133/2021, ETP, TR, IMR, Súmula 269 TCU). "
        "Forneça respostas analíticas, estruturadas e com rigor técnico."
    )
    full_prompt = f"{system_prompt}\n\nContexto: {contexto}\n\nDemanda: {prompt}"
    
    # Tenta usar agente-engenharia ou qwen2.5-coder:14b
    payload = {
        "model": "agente-engenharia:latest",
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.15, "num_ctx": 16384}
    }
    resp = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=12)
    resp.raise_for_status()
    return {"resposta": resp.json().get("response", ""), "modelo": "agente-engenharia:latest", "nivel": 1}