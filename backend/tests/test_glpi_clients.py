import sys
from pathlib import Path

import pytest
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import glpi_clients as g  # noqa: E402

PROD = {"GLPI_PROD_BASE_URL": "https://prod/apirest.php", "GLPI_PROD_APP_TOKEN": "pa", "GLPI_PROD_USER_TOKEN": "pu"}
LOCAL = {"GLPI_LOCAL_BASE_URL": "http://local/apirest.php", "GLPI_LOCAL_APP_TOKEN": "la", "GLPI_LOCAL_USER_TOKEN": "lu"}


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
    for key in PROD:
        monkeypatch.delenv(key)
    _set(monkeypatch, LOCAL)
    assert g.get_write_client().base_url == "http://local/apirest.php"


def test_local_write_does_not_require_absent_prod_config(monkeypatch):
    _set(monkeypatch, LOCAL)
    assert g.get_write_client().base_url == "http://local/apirest.php"


def test_write_rejects_prod_url(monkeypatch):
    _set(
        monkeypatch,
        {**PROD, "GLPI_PROD_BASE_URL": "https://PROD:443/apirest.php/"},
        {**LOCAL, "GLPI_LOCAL_BASE_URL": "https://prod/apirest.php"},
    )
    with pytest.raises(g.GlpiConfigError):
        g.get_write_client()


@pytest.mark.parametrize(
    "local",
    [
        {"GLPI_LOCAL_APP_TOKEN": "pa"},
        {"GLPI_LOCAL_USER_TOKEN": "pu"},
    ],
)
def test_write_rejects_repeated_tokens(monkeypatch, local):
    _set(monkeypatch, PROD, {**LOCAL, **local})
    with pytest.raises(g.GlpiConfigError, match="Tokens"):
        g.get_write_client()


def test_partial_prod_config_is_not_ignored_for_local_write(monkeypatch):
    _set(monkeypatch, LOCAL, {"GLPI_PROD_BASE_URL": "https://prod/apirest.php"})
    with pytest.raises(g.GlpiConfigError, match="GLPI_PROD_APP_TOKEN"):
        g.get_write_client()


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("GLPI_PROD_BASE_URL", "prod/apirest.php"),
        ("GLPI_PROD_BASE_URL", "ftp://prod/apirest.php"),
        ("GLPI_PROD_BASE_URL", "http://prod/apirest.php"),
        ("GLPI_LOCAL_BASE_URL", "local/apirest.php"),
        ("GLPI_LOCAL_BASE_URL", "https://local/apirest.php?token=hidden"),
    ],
)
def test_invalid_base_urls_fail_without_exposing_values(monkeypatch, key, value):
    env = dict(PROD if key.startswith("GLPI_PROD") else LOCAL)
    env[key] = value
    _set(monkeypatch, env)
    with pytest.raises(g.GlpiConfigError) as error:
        (g.get_read_client() if key.startswith("GLPI_PROD") else g.get_write_client())
    assert value not in str(error.value)


def test_prod_client_issues_only_get(monkeypatch):
    _set(monkeypatch, PROD)
    calls = []
    monkeypatch.setattr(g._BaseGlpiClient, "_request", lambda self, m, p, **kw: calls.append(m))
    g.get_read_client().get("/Ticket")
    assert calls == ["GET"]


def test_prod_client_rejects_write_methods_and_absolute_destinations(monkeypatch):
    _set(monkeypatch, PROD)
    client = g.get_read_client()
    assert not hasattr(client, "write")
    for method in ("POST", "PUT", "PATCH", "DELETE"):
        with pytest.raises(ValueError, match="somente GET"):
            client._request(method, "Ticket")
    with pytest.raises(ValueError, match="relativo"):
        client.get("https://local/Ticket")


def test_mock_transport_proves_prod_get_and_local_write_hosts(monkeypatch):
    _set(monkeypatch, PROD, LOCAL)
    requests = []
    real_client = httpx.Client

    def capture(request):
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    def mock_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(capture)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(g.httpx, "Client", mock_client)
    g.get_read_client().get("Ticket")
    g.get_write_client().write("POST", "Ticket", json={"name": "local test"})

    assert [(request.method, request.url.host) for request in requests] == [
        ("GET", "prod"),
        ("POST", "local"),
    ]
    assert requests[0].headers["App-Token"] == PROD["GLPI_PROD_APP_TOKEN"]
    assert requests[0].headers["Authorization"] == f"user_token {PROD['GLPI_PROD_USER_TOKEN']}"
    assert requests[1].headers["App-Token"] == LOCAL["GLPI_LOCAL_APP_TOKEN"]
    assert requests[1].headers["Authorization"] == f"user_token {LOCAL['GLPI_LOCAL_USER_TOKEN']}"


def test_config_repr_hides_secrets(monkeypatch):
    _set(monkeypatch, PROD)
    assert "pu" not in repr(g.load_prod_config()).replace("prod", "")
