import os
import requests

NEWAPI_URL = os.getenv("NEWAPI_URL", "http://127.0.0.1:3001/v1")
NEWAPI_KEY = os.getenv("NEW_API_KEY", "")

def testar_conexao_newapi() -> dict:
    try:
        headers = {"Authorization": f"Bearer {NEWAPI_KEY}"} if NEWAPI_KEY else {}
        resp = requests.get(f"{NEWAPI_URL}/models", headers=headers, timeout=2)
        online = resp.status_code in [200, 401]
        return {"sistema": "New API Gateway", "porta": 3001, "status": "online" if online else "offline", "http_code": resp.status_code}
    except Exception as e:
        return {"sistema": "New API Gateway", "porta": 3001, "status": "offline", "erro": str(e)}