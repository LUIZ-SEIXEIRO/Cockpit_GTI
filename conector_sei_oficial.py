# -*- coding: utf-8 -*-
"""Cliente oficial REST para a API sei-processos (Portal de APIs Prodesp / IDP.SP)."""

from dataclasses import dataclass
import json
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib import error, parse, request
import uuid


DEFAULT_TOKEN_URL = "https://idp.sp.gov.br/auth/realms/idpsp/protocol/openid-connect/token"
DEFAULT_BASE_URL = "https://sei-processos.api.rota.sp.gov.br"
DEFAULT_UNIDADE_ID = "110050725"

ALLOWED_HOSTS = frozenset({
    "idp.sp.gov.br",
    "rhsso.idp-hml.sp.gov.br",
    "sei-processos.api.rota.sp.gov.br",
    "sei-processos.api-hml.rota.sp.gov.br",
})


class SEIOfficialAPIError(RuntimeError):
    """Erro estruturado ao comunicar com o IDP.SP ou sei-processos."""

    def __init__(self, message: str, status_code: Optional[int] = None, trace_id: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.trace_id = trace_id


@dataclass(frozen=True)
class SEIOfficialConfig:
    token_url: str
    base_url: str
    client_id: str
    client_secret: str
    sigla_sistema: str
    identificacao_servico: str
    id_unidade: str = DEFAULT_UNIDADE_ID
    timeout_s: int = 20

    @classmethod
    def from_env(cls) -> "SEIOfficialConfig":
        return cls(
            token_url=os.getenv("SEI_API_TOKEN_URL", DEFAULT_TOKEN_URL).strip(),
            base_url=os.getenv("SEI_API_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/"),
            client_id=os.getenv("SEI_API_CLIENT_ID", "").strip(),
            client_secret=os.getenv("SEI_API_CLIENT_SECRET", "").strip(),
            sigla_sistema=os.getenv("SEI_API_SIGLA_SISTEMA", "").strip(),
            identificacao_servico=os.getenv("SEI_API_IDENTIFICACAO_SERVICO", "").strip(),
            id_unidade=os.getenv("SEI_ID_UNIDADE", DEFAULT_UNIDADE_ID).strip() or DEFAULT_UNIDADE_ID,
            timeout_s=max(5, min(60, int(os.getenv("SEI_API_TIMEOUT_S", "20")))),
        )

    def missing_fields(self) -> List[str]:
        faltantes = []
        if not self.client_id:
            faltantes.append("SEI_API_CLIENT_ID")
        if not self.client_secret:
            faltantes.append("SEI_API_CLIENT_SECRET")
        if not self.sigla_sistema:
            faltantes.append("SEI_API_SIGLA_SISTEMA")
        if not self.identificacao_servico:
            faltantes.append("SEI_API_IDENTIFICACAO_SERVICO")
        return faltantes

    def is_ready(self) -> bool:
        return len(self.missing_fields()) == 0


def validar_url_oficial(url: str) -> str:
    parsed = parse.urlparse((url or "").strip())
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise SEIOfficialAPIError(f"URL invalida ou sem HTTPS: {url}")
    if parsed.hostname.lower() not in ALLOWED_HOSTS:
        raise SEIOfficialAPIError(f"Host fora da allowlist oficial SP: {parsed.hostname}")
    return url.strip()


def normalizar_protocolo(protocolo: str) -> str:
    digitos = re.sub(r"\D", "", protocolo or "")
    if not digitos:
        raise SEIOfficialAPIError("Protocolo SEI invalido ou vazio.")
    return digitos


class SEIOfficialClient:
    """Cliente OAuth2 + REST para sei-processos v1.0.8."""

    def __init__(self, config: Optional[SEIOfficialConfig] = None):
        self.config = config or SEIOfficialConfig.from_env()
        self._lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

    def status_configuracao(self) -> Dict[str, Any]:
        faltantes = self.config.missing_fields()
        return {
            "pronta": len(faltantes) == 0,
            "base_url": self.config.base_url,
            "token_url": self.config.token_url,
            "id_unidade": self.config.id_unidade,
            "client_id_configurado": bool(self.config.client_id),
            "sigla_sistema_configurada": bool(self.config.sigla_sistema),
            "faltantes": faltantes,
        }

    def obter_token(self, force_refresh: bool = False) -> str:
        if not self.config.client_id or not self.config.client_secret:
            raise SEIOfficialAPIError("Credenciais IDP.SP ausentes (SEI_API_CLIENT_ID / SEI_API_CLIENT_SECRET).")

        validar_url_oficial(self.config.token_url)

        with self._lock:
            agora = time.time()
            if not force_refresh and self._access_token and agora < (self._expires_at - 60):
                return self._access_token

            payload = parse.urlencode({
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }).encode("utf-8")

            req = request.Request(
                self.config.token_url,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=self.config.timeout_s) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
            except error.HTTPError as exc:
                raise SEIOfficialAPIError(f"Falha OAuth2 IDP.SP (HTTP {exc.code}).", status_code=exc.code) from exc
            except Exception as exc:
                raise SEIOfficialAPIError(f"Erro de rede ao autenticar no IDP.SP: {exc}") from exc

            token = body.get("access_token")
            if not token:
                raise SEIOfficialAPIError("Resposta do IDP.SP sem access_token.")

            expires_in = int(body.get("expires_in", 300) or 300)
            self._access_token = token
            self._expires_at = agora + expires_in
            return token

    def _request(self, method: str, path: str, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.config.is_ready():
            faltantes = ", ".join(self.config.missing_fields())
            raise SEIOfficialAPIError(f"Configuracao incompleta da API SEI oficial. Faltantes: {faltantes}")

        url = f"{self.config.base_url}{path}"
        if query:
            filtrados = {k: v for k, v in query.items() if v is not None and v != ""}
            if filtrados:
                url = f"{url}?{parse.urlencode(filtrados)}"
        validar_url_oficial(url)

        for tentativa in range(2):
            token = self.obter_token(force_refresh=(tentativa == 1))
            trace_id = str(uuid.uuid4())
            headers = {
                "Authorization": f"Bearer {token}",
                "X-TraceId-SP": trace_id,
                "X-SiglaSistema": self.config.sigla_sistema,
                "X-IdentificacaoServico": self.config.identificacao_servico,
                "X-IdUnidade": self.config.id_unidade,
                "Accept": "application/json",
            }
            req = request.Request(url, method=method.upper(), headers=headers)
            try:
                with request.urlopen(req, timeout=self.config.timeout_s) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except error.HTTPError as exc:
                if exc.code == 401 and tentativa == 0:
                    continue
                detalhe = exc.read().decode("utf-8", errors="ignore")[:300]
                raise SEIOfficialAPIError(
                    f"Erro HTTP {exc.code} em {path}: {detalhe}",
                    status_code=exc.code,
                    trace_id=trace_id,
                ) from exc
            except Exception as exc:
                raise SEIOfficialAPIError(f"Falha de comunicacao em {path}: {exc}", trace_id=trace_id) from exc

        raise SEIOfficialAPIError("Falha de autenticacao apos renovacao de token.")

    def listar_processos_unidade(
        self,
        start: int = 0,
        limit: int = 50,
        tipo: Optional[str] = None,
        apenas_meus: bool = False,
        retornar_marcadores: bool = False,
        retornar_status: bool = False,
    ) -> Dict[str, Any]:
        limit_seguro = max(1, min(100, int(limit)))
        query = {
            "start": max(0, int(start)),
            "limit": limit_seguro,
            "tipo": tipo,
            "apenasMeus": "S" if apenas_meus else "N",
            "sinRetornarMarcadores": "S" if retornar_marcadores else "N",
            "sinRetornarStatus": "S" if retornar_status else "N",
        }
        return self._request("GET", "/processos", query=query)

    def consultar_processo(
        self,
        protocolo: str,
        sin_ultimo_andamento: bool = True,
        sin_unidades_abertas: bool = True,
    ) -> Dict[str, Any]:
        proto = normalizar_protocolo(protocolo)
        query = {
            "sinRetornarUltimoAndamento": str(bool(sin_ultimo_andamento)).lower(),
            "sinRetornarUnidadesProcedimentoAberto": str(bool(sin_unidades_abertas)).lower(),
        }
        return self._request("GET", f"/processos/{proto}", query=query)

    def listar_documentos_processo(self, protocolo: str, start: int = 0, limit: int = 50) -> Dict[str, Any]:
        proto = normalizar_protocolo(protocolo)
        return self._request(
            "GET",
            f"/processos/{proto}/documentos",
            query={"start": max(0, int(start)), "limit": max(1, min(100, int(limit)))},
        )

    def listar_andamentos_processo(self, protocolo: str, retorna_atributos: bool = False) -> Dict[str, Any]:
        proto = normalizar_protocolo(protocolo)
        return self._request(
            "GET",
            "/processos/andamentos",
            query={"protocoloProcedimento": proto, "retornaAtributos": "S" if retorna_atributos else "N"},
        )
