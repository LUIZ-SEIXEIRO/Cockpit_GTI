import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

os.environ.update(DB_USER="u", DB_PASSWORD="p", DB_NAME="n", DB_HOST="localhost")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "online"


def test_db_health_ok():
    with patch.object(main, "check_database_connection"):
        r = client.get("/api/health/db")
    assert r.status_code == 200
    assert r.json() == {"status": "online", "database": "connected"}


def test_db_health_failure_is_generic():
    with patch.object(main, "check_database_connection", side_effect=Exception("secret-detail")):
        r = client.get("/api/health/db")
    assert r.status_code == 503
    assert "secret-detail" not in r.text


def test_glpi_tickets_returns_dashboard_fields_and_applies_limit():
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.execute.return_value.mappings.return_value.all.return_value = [
        {
            "id": 42,
            "name": "Falha de acesso",
            "status": 2,
            "priority": 5,
            "date": datetime(2026, 10, 26, 12, 0),
            "category": "Sistemas",
        }
    ]
    with patch.object(main.engine, "connect", return_value=connection):
        response = client.get("/api/glpi/chamados?limit=25")

    assert response.status_code == 200
    assert response.json() == {
        "dados": [
            {
                "id": 42,
                "nome": "Falha de acesso",
                "status": "Em atendimento",
                "prioridade": 5,
                "criado_em": "2026-10-26T12:00:00",
                "Eixo_Gestao": "Sistemas",
                "Farol_Criticidade": "1 - Intervenção",
                "Classificacao_Risco": "Crítico",
            }
        ]
    }
    assert connection.execute.call_args.args[1] == {"limit": 25}


def test_glpi_tickets_rejects_out_of_range_limit():
    assert client.get("/api/glpi/chamados?limit=0").status_code == 422
    assert client.get("/api/glpi/chamados?limit=201").status_code == 422


def test_glpi_tickets_database_failure_is_generic():
    with patch.object(main.engine, "connect", side_effect=Exception("secret-detail")):
        response = client.get("/api/glpi/chamados")

    assert response.status_code == 503
    assert "secret-detail" not in response.text
