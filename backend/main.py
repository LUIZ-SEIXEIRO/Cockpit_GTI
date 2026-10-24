from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="SP Águas - Cockpit de Gestão")

# Caminho absoluto para a pasta frontend (um nível acima do backend)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Monta a pasta frontend na raiz para servir CSS, JS e Imagens
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_painel():
    """Entrega a casca principal da SPA (painel.html)"""
    return FileResponse(os.path.join(FRONTEND_DIR, "painel.html"))

@app.get("/api/health")
async def health_check():
    """Rota simples para verificar se o backend está online"""
    return {"status": "online", "service": "FastAPI SP-Águas"}
