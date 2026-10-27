"""Configuracao e clientes GLPI separados.

GLPI oficial (producao): SOMENTE LEITURA. O cliente nao expoe metodos de escrita.
GLPI local: destino de todas as gravacoes do Cockpit (integracao ainda nao implementada;
os endpoints de escrita ficam para as Sprints 2/3).
Nao ha fallback entre os dois ambientes.
"""
import os
from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlsplit, urlunsplit

import httpx

PROD_PREFIX = "GLPI_PROD"
LOCAL_PREFIX = "GLPI_LOCAL"
_FIELDS = ("BASE_URL", "APP_TOKEN", "USER_TOKEN")


class GlpiConfigError(RuntimeError):
    """Configuracao GLPI ausente ou invalida (nunca inclui valores de segredos)."""


@dataclass(frozen=True)
class GlpiConfig:
    name: str
    base_url: str
    app_token: str = ""
    user_token: str = ""

    def __repr__(self) -> str:
        return f"GlpiConfig(name={self.name!r}, base_url={self.base_url!r})"


def _load(prefix: str, name: str) -> GlpiConfig:
    values = {f: (os.getenv(f"{prefix}_{f}") or "").strip() for f in _FIELDS}
    missing = [f"{prefix}_{f}" for f, v in values.items() if not v]
    if missing:
        raise GlpiConfigError(f"Configuracao GLPI {name} incompleta. Defina: {', '.join(missing)}")
    base_url = _normalize_base_url(values["BASE_URL"], f"{prefix}_BASE_URL", prefix == PROD_PREFIX)
    return GlpiConfig(name, base_url, values["APP_TOKEN"], values["USER_TOKEN"])


def _normalize_base_url(value: str, field: str, production: bool = False) -> str:
    if any(char.isspace() for char in value):
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida")
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida") from None
    scheme = parsed.scheme.lower()
    if (
        scheme not in {"http", "https"}
        or not parsed.netloc
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida")
    try:
        normalized_host = hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida") from None
    if not normalized_host:
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida")
    if ":" in normalized_host:
        normalized_host = f"[{normalized_host}]"
    if port is not None and not 1 <= port <= 65535:
        raise GlpiConfigError(f"{field} deve ser uma URL absoluta valida")
    default_port = 443 if scheme == "https" else 80
    netloc = normalized_host if port in (None, default_port) else f"{normalized_host}:{port}"
    if production and scheme != "https":
        try:
            is_loopback = normalized_host.strip("[]") == "localhost" or ip_address(
                normalized_host.strip("[]")
            ).is_loopback
        except ValueError:
            is_loopback = False
        if not is_loopback:
            raise GlpiConfigError(f"{field} deve usar HTTPS")
    path = parsed.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))


def load_prod_config() -> GlpiConfig:
    return _load(PROD_PREFIX, "producao")


def load_local_config() -> GlpiConfig:
    return _load(LOCAL_PREFIX, "local")


def _validate_distinct(prod: GlpiConfig, local: GlpiConfig) -> None:
    prod_url = _normalize_base_url(prod.base_url, "GLPI_PROD_BASE_URL", True)
    local_url = _normalize_base_url(local.base_url, "GLPI_LOCAL_BASE_URL")
    if prod_url == local_url:
        raise GlpiConfigError("GLPI_LOCAL_BASE_URL nao pode ser igual a GLPI_PROD_BASE_URL")
    if prod.user_token == local.user_token or prod.app_token == local.app_token:
        raise GlpiConfigError("Tokens do GLPI local devem ser distintos dos de producao")


def _load_optional_prod_config() -> GlpiConfig | None:
    values = [os.getenv(f"{PROD_PREFIX}_{field}") for field in _FIELDS]
    if not any((value or "").strip() for value in values):
        return None
    return load_prod_config()


def _validate_endpoint(path: str) -> str:
    parsed = urlsplit(path)
    if (
        not path
        or parsed.scheme
        or parsed.netloc
        or parsed.fragment
        or "\\" in path
        or path.startswith("//")
    ):
        raise ValueError("O caminho GLPI deve ser relativo ao cliente")
    return path


class _BaseGlpiClient:
    def __init__(self, config: GlpiConfig, timeout: float = 15.0):
        self._config = config
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def _headers(self, session_token: str | None = None) -> dict:
        headers = {"App-Token": self._config.app_token}
        if session_token:
            headers["Session-Token"] = session_token
        else:
            headers["Authorization"] = f"user_token {self._config.user_token}"
        return headers

    def _request(self, method: str, path: str, **kwargs):
        path = _validate_endpoint(path)
        with httpx.Client(base_url=self._config.base_url, timeout=self._timeout) as http:
            return http.request(method, path, **kwargs)


class GlpiProdReadOnlyClient(_BaseGlpiClient):
    """Cliente do GLPI oficial: apenas GET. Nao existe caminho de escrita."""

    def _request(self, method: str, path: str, **kwargs):
        if method.upper() != "GET":
            raise ValueError("O GLPI oficial permite somente GET")
        return super()._request("GET", path, **kwargs)

    def get(self, path: str, session_token: str | None = None, **kwargs):
        return self._request("GET", path, headers=self._headers(session_token), **kwargs)


class GlpiLocalClient(_BaseGlpiClient):
    """Cliente do GLPI local (destino das gravacoes). Integracao completa: Sprint 2/3."""

    def get(self, path: str, session_token: str | None = None, **kwargs):
        return self._request("GET", path, headers=self._headers(session_token), **kwargs)

    def write(self, method: str, path: str, session_token: str | None = None, **kwargs):
        if method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("Metodo de escrita invalido")
        return self._request(method.upper(), path, headers=self._headers(session_token), **kwargs)


def get_read_client() -> GlpiProdReadOnlyClient:
    return GlpiProdReadOnlyClient(load_prod_config())


def get_write_client() -> GlpiLocalClient:
    """Retorna somente o cliente local; sem fallback para producao."""
    local = load_local_config()
    prod = _load_optional_prod_config()
    if prod is not None:
        _validate_distinct(prod, local)
    return GlpiLocalClient(local)
