import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sqlalchemy import text

from backenddatabase_mariadb import check_database_connection, engine

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


@app.get("/api/glpi/chamados")
def list_glpi_tickets(limit: int = Query(default=50, ge=1, le=200)):
    """Retorna campos resumidos de chamados ativos para o painel."""
    query = text(
        """
        SELECT tickets.id, tickets.name, tickets.status, tickets.priority,
               tickets.date, categories.name AS category
        FROM glpi_tickets AS tickets
        LEFT JOIN glpi_itilcategories AS categories
            ON categories.id = tickets.itilcategories_id
        WHERE tickets.is_deleted = 0
        ORDER BY tickets.date DESC, tickets.id DESC
        LIMIT :limit
        """
    )
    try:
        with engine.connect() as connection:
            tickets = connection.execute(query, {"limit": limit}).mappings().all()
    except Exception:
        logger.exception("Falha ao consultar chamados do GLPI")
        raise HTTPException(status_code=503, detail="Dados do GLPI indisponíveis")

    status_labels = {
        1: "Novo",
        2: "Em atendimento",
        3: "Planejado",
        4: "Pendente",
        5: "Solucionado",
        6: "Fechado",
    }
    priority_labels = {
        1: ("Baixo", "4 - Fluxo Normal"),
        2: ("Baixo", "4 - Fluxo Normal"),
        3: ("Médio", "3 - Monitoramento"),
        4: ("Alto", "2 - Saneamento"),
        5: ("Crítico", "1 - Intervenção"),
        6: ("Crítico", "1 - Intervenção"),
    }
    dados = []
    for ticket in tickets:
        priority = int(ticket["priority"])
        risk, criticality = priority_labels.get(
            priority, ("Não classificado", "Não classificado")
        )
        dados.append(
            {
                "id": ticket["id"],
                "nome": ticket["name"] or "Sem título",
                "status": status_labels.get(ticket["status"], "Desconhecido"),
                "prioridade": priority,
                "criado_em": ticket["date"],
                "Eixo_Gestao": ticket["category"] or "Sem categoria",
                "Farol_Criticidade": criticality,
                "Classificacao_Risco": risk,
            }
        )
    return {"dados": dados}
