import logging

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backenddatabase_mariadb import check_database_connection

logger = logging.getLogger(__name__)

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


@app.get("/api/health/db")
def database_health_check():
    """Verifica se o backend consegue executar SELECT 1 no MariaDB"""
    try:
        check_database_connection()
    except Exception:
        logger.exception("Falha na verificação de saúde do banco de dados")
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")
    return {"status": "online", "database": "connected"}
