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
