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


def test_fastapi_is_the_compose_runtime():
    from fastapi import FastAPI

    repository_root = Path(__file__).resolve().parents[2]
    compose = (repository_root / "docker-compose.yml").read_text(encoding="utf-8")
    dockerfile = (repository_root / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert isinstance(main.app, FastAPI)
    assert 'context: ./backend' in compose
    for variable in ("GLPI_PROD_BASE_URL", "GLPI_PROD_APP_TOKEN", "GLPI_PROD_USER_TOKEN"):
        assert f"{variable}: ${{{variable}:-}}" in compose
    assert 'CMD ["uvicorn", "main:app",' in dockerfile
    assert not (repository_root / "main.py").exists()


def test_optional_glpi_local_compose_is_isolated():
    repository_root = Path(__file__).resolve().parents[2]
    compose = (repository_root / "docker-compose.yml").read_text(encoding="utf-8")

    assert "image: glpi/glpi:11.0.7" in compose
    assert "image: mariadb:10.11" in compose
    assert "glpi-local-db:" in compose
    assert "profiles:\n      - glpi-local" in compose
    assert '"127.0.0.1:${GLPI_LOCAL_PORT:-8081}:80"' in compose
    assert "glpi_local_db_data:/var/lib/mysql" in compose
    assert "glpi_local_data:/var/glpi" in compose
    assert "GLPI_LOCAL_BASE_URL: ${GLPI_LOCAL_BASE_URL:-http://glpi-local/apirest.php}" in compose
    assert "GLPI_LOCAL_APP_TOKEN: ${GLPI_LOCAL_APP_TOKEN:-}" in compose
    assert "GLPI_LOCAL_USER_TOKEN: ${GLPI_LOCAL_USER_TOKEN:-}" in compose
    backend_service = compose.split("  backend:\n", 1)[1].split("  glpi-local-db:\n", 1)[0]
    database_service = compose.split("  glpi-local-db:\n", 1)[1].split("  glpi-local:\n", 1)[0]
    glpi_service = compose.split("  glpi-local:\n", 1)[1].split("\nvolumes:\n", 1)[0]
    assert "- glpi-local-api" in backend_service
    assert "- glpi-local-db" not in backend_service
    assert "- glpi-local-db" in database_service
    assert "glpi-local-api:" in glpi_service
    assert "glpi-local-db:" in glpi_service


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
