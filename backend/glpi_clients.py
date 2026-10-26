"""Configuracao e clientes GLPI separados.

GLPI oficial (producao): SOMENTE LEITURA. O cliente nao expoe metodos de escrita.
GLPI local: destino de todas as gravacoes do Cockpit (integracao ainda nao implementada;
os endpoints de escrita ficam para as Sprints 2/3).
Nao ha fallback entre os dois ambientes.
"""
import os
from dataclasses import dataclass

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
    return GlpiConfig(name, values["BASE_URL"].rstrip("/"), values["APP_TOKEN"], values["USER_TOKEN"])


def load_prod_config() -> GlpiConfig:
    return _load(PROD_PREFIX, "producao")


def load_local_config() -> GlpiConfig:
    return _load(LOCAL_PREFIX, "local")


def _validate_distinct(prod: GlpiConfig, local: GlpiConfig) -> None:
    if prod.base_url == local.base_url:
        raise GlpiConfigError("GLPI_LOCAL_BASE_URL nao pode ser igual a GLPI_PROD_BASE_URL")
    if prod.user_token == local.user_token or prod.app_token == local.app_token:
        raise GlpiConfigError("Tokens do GLPI local devem ser distintos dos de producao")


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
        with httpx.Client(base_url=self._config.base_url, timeout=self._timeout) as http:
            return http.request(method, path, **kwargs)


class GlpiProdReadOnlyClient(_BaseGlpiClient):
    """Cliente do GLPI oficial: apenas GET. Nao existe caminho de escrita."""

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
    prod_url = (os.getenv(f"{PROD_PREFIX}_BASE_URL") or "").strip().rstrip("/")
    if prod_url and prod_url == local.base_url:
        raise GlpiConfigError("GLPI_LOCAL_BASE_URL nao pode apontar para o GLPI de producao")
    return GlpiLocalClient(local)
