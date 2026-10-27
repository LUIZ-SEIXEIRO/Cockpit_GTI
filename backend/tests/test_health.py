import os
import sys
from pathlib import Path
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


def test_mesa_persistence_fails_closed_without_auth_and_project_setup():
    r = client.get("/api/mesa/minhas-tarefas")
    assert r.status_code == 503
    assert r.json() == {
        "detail": "Persistência da Mesa indisponível: autenticação e projeto GLPI local não configurados."
    }


def test_mesa_script_matches_panel_and_router():
    repository_root = Path(__file__).resolve().parents[2]
    panel = (repository_root / "frontend" / "painel.html").read_text(encoding="utf-8")
    mesa_script = repository_root / "frontend" / "abas" / "aba_06_mesa_trabalho.js"
    router = (repository_root / "frontend" / "abas" / "00_roteador_abas.js").read_text(encoding="utf-8")

    assert '<script src="/static/abas/aba_06_mesa_trabalho.js"></script>' in panel
    assert mesa_script.is_file()
    assert "window.initAba_mesa" in mesa_script.read_text(encoding="utf-8")
    assert "const initFunctionName = 'initAba_' + tabId;" in router


def test_fastapi_is_the_compose_runtime():
    from fastapi import FastAPI

    repository_root = Path(__file__).resolve().parents[2]
    compose = (repository_root / "docker-compose.yml").read_text(encoding="utf-8")
    dockerfile = (repository_root / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert isinstance(main.app, FastAPI)
    assert 'context: ./backend' in compose
    assert 'CMD ["uvicorn", "main:app",' in dockerfile
    assert not (repository_root / "main.py").exists()


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


def test_compose_glpi_local_is_isolated():
    repository_root = Path(__file__).resolve().parents[2]
    compose = (repository_root / "docker-compose.yml").read_text(encoding="utf-8")
    start = compose.index("  glpi-local:")
    end = compose.index("\nvolumes:", start)
    glpi = compose[start:end]
    glpi_db = compose[compose.index("  glpi-db:"):start]

    assert '"8088:80"' in glpi
    assert "glpi_local_data:/var/glpi" in glpi
    assert "glpi_local_db:/var/lib/mysql" in glpi_db
    assert ":latest" not in compose
    assert "image: ghcr.io/glpi-project/glpi:12.0.0" in glpi
    assert "GLPI_DB_HOST: glpi-db" in glpi
    for service in (glpi, glpi_db):
        assert "${DB_" not in service
        assert "GLPI_PROD" not in service
    assert "${GLPI_LOCAL_DB_PASSWORD:?" in glpi
    assert "${GLPI_LOCAL_DB_ROOT_PASSWORD:?" in glpi_db
    assert "condition: service_healthy" in glpi
