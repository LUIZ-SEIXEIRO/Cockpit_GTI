import sys
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import glpi_clients as g  # noqa: E402

PROD = {"GLPI_PROD_BASE_URL": "https://prod/apirest.php", "GLPI_PROD_APP_TOKEN": "pa", "GLPI_PROD_USER_TOKEN": "pu"}
LOCAL = {"GLPI_LOCAL_BASE_URL": "http://glpi-local/apirest.php", "GLPI_LOCAL_APP_TOKEN": "la", "GLPI_LOCAL_USER_TOKEN": "lu"}


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    for k in [*PROD, *LOCAL]:
        monkeypatch.delenv(k, raising=False)


def _set(monkeypatch, *envs):
    for e in envs:
        for k, v in e.items():
            monkeypatch.setenv(k, v)


def test_incomplete_config_fails_clearly(monkeypatch):
    with pytest.raises(g.GlpiConfigError, match="GLPI_PROD_BASE_URL"):
        g.get_read_client()
    with pytest.raises(g.GlpiConfigError, match="GLPI_LOCAL_APP_TOKEN"):
        _set(monkeypatch, {"GLPI_LOCAL_BASE_URL": "x", "GLPI_LOCAL_USER_TOKEN": "y"})
        g.get_write_client()


def test_invalid_local_url_fails_closed(monkeypatch):
    _set(monkeypatch, {**LOCAL, "GLPI_LOCAL_BASE_URL": "glpi-local/apirest.php"})
    with pytest.raises(g.GlpiConfigError, match="GLPI_LOCAL_BASE_URL"):
        g.get_write_client()


def test_read_uses_only_prod(monkeypatch):
    _set(monkeypatch, PROD)
    c = g.get_read_client()
    assert c.base_url == "https://prod/apirest.php"
    assert not hasattr(c, "write")
    assert not any(hasattr(c, m) for m in ("post", "put", "delete", "patch"))


def test_write_uses_only_local_and_no_prod_fallback(monkeypatch):
    _set(monkeypatch, PROD)
    with pytest.raises(g.GlpiConfigError):
        g.get_write_client()
    _set(monkeypatch, LOCAL)
    assert g.get_write_client().base_url == "http://glpi-local/apirest.php"


def test_write_rejects_prod_url(monkeypatch):
    _set(monkeypatch, PROD, {**LOCAL, "GLPI_LOCAL_BASE_URL": "https://prod/apirest.php/"})
    with pytest.raises(g.GlpiConfigError):
        g.get_write_client()


def test_write_rejects_unapproved_remote_url_without_prod_config(monkeypatch):
    _set(monkeypatch, {**LOCAL, "GLPI_LOCAL_BASE_URL": "https://glpi.example/apirest.php"})
    with pytest.raises(g.GlpiConfigError):
        g.get_write_client()


def test_prod_client_issues_only_get(monkeypatch):
    _set(monkeypatch, PROD)
    calls = []
    monkeypatch.setattr(g._BaseGlpiClient, "_request", lambda self, m, p, **kw: calls.append(m))
    g.get_read_client().get("/Ticket")
    assert calls == ["GET"]


@pytest.mark.parametrize(
    ("method", "path"),
    [("POST", "ProjectTask/"), ("PUT", "ProjectTask/42")],
)
def test_local_write_uses_mock_transport_and_never_targets_prod(monkeypatch, method, path):
    _set(monkeypatch, PROD, LOCAL)
    requests = []
    transport = httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(200, json={"ok": True})
    )
    client_class = httpx.Client
    monkeypatch.setattr(
        g.httpx,
        "Client",
        lambda **kwargs: client_class(transport=transport, **kwargs),
    )

    response = g.get_write_client().write(method, path, json={"input": {"name": "offline test"}})

    assert response.status_code == 200
    assert len(requests) == 1
    assert requests[0].method == method
    assert str(requests[0].url) == f"http://glpi-local/apirest.php/{path}"
    assert requests[0].url.host != "prod"


def test_config_repr_hides_secrets(monkeypatch):
    _set(monkeypatch, PROD)
    assert "pu" not in repr(g.load_prod_config()).replace("prod", "")
