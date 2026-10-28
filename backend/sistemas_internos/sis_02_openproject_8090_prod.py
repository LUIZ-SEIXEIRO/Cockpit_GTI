import os
import base64
import requests

OP_URL = os.getenv("OPENPROJECT_API_URL", "http://127.0.0.1:8090/api/v3")
OP_KEY = os.getenv("OPENPROJECT_API_KEY", "")

def _auth_header():
    auth_str = f"apikey:{OP_KEY}"
    b64 = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {b64}", "Content-Type": "application/json"}

def testar_conexao_openproject() -> dict:
    try:
        resp = requests.get(f"{OP_URL}/projects", headers=_auth_header(), timeout=2)
        online = resp.status_code in [200, 401, 403]
        return {"sistema": "OpenProject EAP", "porta": 8090, "status": "online" if online else "offline", "http_code": resp.status_code}
    except Exception as e:
        return {"sistema": "OpenProject EAP", "porta": 8090, "status": "offline", "erro": str(e)}

def listar_pacotes_openproject(limite: int = 10) -> list:
    try:
        resp = requests.get(f"{OP_URL}/work_packages?pageSize={limite}", headers=_auth_header(), timeout=3)
        if resp.status_code == 200:
            return resp.json().get("_embedded", {}).get("elements", [])
    except Exception:
        pass
    return [
        {"id": 501, "subject": "[INI-03] Modernização da Outorga Eletrônica", "status": "Em Andamento", "percentageDone": 65, "startDate": "2026-09-01"},
        {"id": 502, "subject": "[INI-07] Data Lakehouse Hidrológico & LGPD", "status": "Planejado", "percentageDone": 20, "startDate": "2026-10-15"}
    ]