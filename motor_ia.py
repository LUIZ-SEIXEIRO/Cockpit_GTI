# -*- coding: utf-8 -*-
import json
import math
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Set
from urllib.parse import urlparse

RE_PROCESSO_SEI = re.compile(r"\b\d{3}\.\d{8}/\d{4}-\d{2}\b")
RE_VALOR_BRL = re.compile(r"R\$\s*\d+(?:\.\d{3})*(?:,\d{2})?")
RE_PRAZO = re.compile(r"\b\d+\s+(?:dias?|meses|m\u00eas|anos?)\b", re.IGNORECASE)
RE_DATA = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")

ENDPOINTS_PADRAO_PERMITIDOS = frozenset({
    ("http", "127.0.0.1", 3001),
    ("http", "localhost", 3001),
    ("http", "127.0.0.1", 11434),
    ("http", "localhost", 11434),
    ("http", "new-api", 3000),
    ("http", "cockpit-gti-newapi", 3000),
    ("http", "ollama", 11434),
    ("http", "cockpit-gti-ollama", 11434),
    ("http", "100.103.100.98", 3001),
    ("http", "100.103.100.98", 11434),
})

DIRETRIZ_GROUNDING_ESTRITO = (
    "[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]\n"
    "1. Responda EXCLUSIVAMENTE com base nos dados verificados presentes no contexto desta conversa.\n"
    "2. Se uma informa\u00e7\u00e3o (n\u00famero de processo SEI, prazo, valor, data, norma ou respons\u00e1vel) n\u00e3o constar no contexto, "
    "declare explicitamente: 'Informa\u00e7\u00e3o n\u00e3o localizada no contexto fornecido.'\n"
    "3. Nunca invente n\u00fameros de processo, datas, valores monet\u00e1rios, m\u00e9tricas ou cita\u00e7\u00f5es legais."
)


def em_container_docker() -> bool:
    return os.path.exists("/.dockerenv")


def obter_endpoint_padrao() -> str:
    env_ep = (os.getenv("IA_DEFAULT_ENDPOINT") or os.getenv("NEW_API_URL") or "").strip()
    if env_ep:
        limpo = env_ep.rstrip("/")
        return limpo if limpo.endswith("/v1") else limpo + "/v1"
    if em_container_docker():
        tem_chave_newapi = bool((os.getenv("NEW_API_KEY") or os.getenv("NEWAPI_API_KEY") or "").strip())
        return "http://new-api:3000/v1" if tem_chave_newapi else "http://ollama:11434/v1"
    return "http://127.0.0.1:3001/v1"


def obter_endpoints_permitidos() -> Set[tuple]:
    permitidos = set(ENDPOINTS_PADRAO_PERMITIDOS)
    env_eps = os.getenv("IA_ALLOWED_ENDPOINTS", "")
    for item in env_eps.split(","):
        item_limpo = item.strip().rstrip("/")
        if not item_limpo:
            continue
        p = urlparse(item_limpo)
        if p.scheme.lower() in ("http", "https") and p.hostname and p.port:
            permitidos.add((p.scheme.lower(), p.hostname.lower(), int(p.port)))
    return permitidos


def normalizar_temperatura(valor: Any, padrao: float = 0.0) -> float:
    if valor is None or valor == "" or isinstance(valor, bool):
        t = padrao
    else:
        try:
            t = float(valor)
        except (TypeError, ValueError, OverflowError):
            t = padrao
    if not math.isfinite(t):
        t = padrao
    if t < 0.0:
        return 0.0
    if t > 0.7:
        return 0.7
    return round(t, 4)


def normalizar_max_tokens(valor: Any, padrao: int = 700) -> int:
    if valor is None or valor == "" or isinstance(valor, bool):
        n = padrao
    else:
        try:
            f = float(valor)
            n = padrao if not math.isfinite(f) else int(f)
        except (TypeError, ValueError, OverflowError):
            n = padrao
    if n < 64:
        return 64
    if n > 4096:
        return 4096
    return n


def validar_endpoint_ia(endpoint: Any, hosts_permitidos: Optional[Iterable[str]] = None) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("Endpoint de IA inválido ou não informado.")
    limpo = endpoint.strip().rstrip("/")
    parsed = urlparse(limpo)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Endpoint de IA inválido: {endpoint}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise PermissionError("Endpoint de IA com credenciais embutidas, query ou fragmento não autorizado.")
    host = (parsed.hostname or "").lower()
    porta = parsed.port
    caminho = parsed.path.rstrip("/")
    if caminho not in ("", "/v1"):
        raise PermissionError(f"Caminho de endpoint de IA não autorizado: {parsed.path}")
    if porta is None or (scheme, host, int(porta)) not in obter_endpoints_permitidos():
        raise PermissionError(f"Endpoint de provedor de IA não autorizado: {scheme}://{host}:{porta}")
    if em_container_docker() and host in ("127.0.0.1", "localhost"):
        if int(porta) == 3001:
            return "http://new-api:3000/v1"
        if int(porta) == 11434:
            return "http://ollama:11434/v1"
    return f"{scheme}://{host}:{int(porta)}/v1"


def sanitizar_mensagens(mensagens: Any) -> List[Dict[str, str]]:
    if not isinstance(mensagens, list) or not mensagens:
        raise ValueError("Lista de mensagens inv\u00e1lida ou vazia.")
    permitidos = {"system", "user", "assistant"}
    limpas: List[Dict[str, str]] = []
    for item in mensagens:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        content = item.get("content")
        if role in permitidos and isinstance(content, str) and content.strip():
            limpas.append({"role": role, "content": content.strip()})
    if not limpas:
        raise ValueError("Nenhuma mensagem v\u00e1lida encontrada no payload.")
    return limpas


def aplicar_guardiao_grounding(mensagens: List[Dict[str, str]]) -> List[Dict[str, str]]:
    outras = [dict(m) for m in mensagens if m["role"] != "system"]
    sys_cliente = [
        m["content"].replace(DIRETRIZ_GROUNDING_ESTRITO, "").replace("[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]", "").strip()
        for m in mensagens
        if m["role"] == "system"
    ]
    sys_limpo = [s for s in sys_cliente if s]
    conteudo_sys = ("\n\n".join(sys_limpo) + "\n\n" + DIRETRIZ_GROUNDING_ESTRITO) if sys_limpo else DIRETRIZ_GROUNDING_ESTRITO
    return [{"role": "system", "content": conteudo_sys}] + outras


def verificar_consistencia_contextual(resposta: str, contexto: str) -> Dict[str, Any]:
    texto_resp = str(resposta or "").strip()
    texto_ctx = str(contexto or "")
    alertas: List[str] = []

    if not texto_resp:
        return {"consistente": False, "alertas": ["Resposta vazia."]}

    procs_fora = sorted(set(RE_PROCESSO_SEI.findall(texto_resp)) - set(RE_PROCESSO_SEI.findall(texto_ctx)))
    if procs_fora:
        alertas.append(f"Processo(s) SEI fora do contexto: {', '.join(procs_fora)}")

    vals_ctx = {re.sub(r"\s+", "", v) for v in RE_VALOR_BRL.findall(texto_ctx)}
    vals_resp = {re.sub(r"\s+", "", v) for v in RE_VALOR_BRL.findall(texto_resp)}
    vals_fora = sorted(vals_resp - vals_ctx)
    if vals_fora:
        alertas.append(f"Valor(es) monet\u00e1rio(s) fora do contexto: {', '.join(vals_fora)}")

    prazos_ctx = {re.sub(r"\s+", " ", p.lower()) for p in RE_PRAZO.findall(texto_ctx)}
    for num_dias in re.findall(r"(?:aging|prazo)[^:\n]*\(dias\)\s*:\s*(\d+)", texto_ctx, re.IGNORECASE):
        prazos_ctx.add(f"{num_dias} dia")
        prazos_ctx.add(f"{num_dias} dias")
    prazos_resp = {re.sub(r"\s+", " ", p.lower()) for p in RE_PRAZO.findall(texto_resp)}
    prazos_fora = sorted(prazos_resp - prazos_ctx)
    if prazos_fora:
        alertas.append(f"Prazo(s) fora do contexto: {', '.join(prazos_fora)}")

    datas_fora = sorted(set(RE_DATA.findall(texto_resp)) - set(RE_DATA.findall(texto_ctx)))
    if datas_fora:
        alertas.append(f"Data(s) fora do contexto: {', '.join(datas_fora)}")

    return {"consistente": len(alertas) == 0, "alertas": alertas}


def executar_chat_ia(
    mensagens: Any,
    endpoint: Optional[str] = None,
    model: str = "qwen2.5:14b",
    api_key: str = "",
    temperature: Any = 0.0,
    max_tokens: Any = 700,
    timeout: int = 45,
    hosts_permitidos: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    ep_alvo = obter_endpoint_padrao() if endpoint is None or endpoint == "" else endpoint
    try:
        endpoint_valido = validar_endpoint_ia(ep_alvo, hosts_permitidos=hosts_permitidos)
        msgs_limpas = sanitizar_mensagens(mensagens)
    except PermissionError as pe:
        return {"sucesso": False, "codigo": 403, "status": "erro", "mensagem": str(pe)}
    except ValueError as ve:
        return {"sucesso": False, "codigo": 400, "status": "erro", "mensagem": str(ve)}

    msgs_protegidas = aplicar_guardiao_grounding(msgs_limpas)
    temp_final = normalizar_temperatura(temperature, padrao=0.0)
    tokens_final = normalizar_max_tokens(max_tokens, padrao=700)

    url = endpoint_valido + "/chat/completions"
    payload = {
        "model": str(model or "qwen2.5:14b"),
        "messages": msgs_protegidas,
        "temperature": temp_final,
        "max_tokens": tokens_final,
    }
    headers_req = {"Content-Type": "application/json"}
    if isinstance(api_key, str) and api_key.strip() and api_key.strip() != "***":
        headers_req["Authorization"] = f"Bearer {api_key.strip()}"

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers_req, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as he:
        cod = he.code if he.code in (400, 401, 403, 404, 429) else 502
        return {"sucesso": False, "codigo": cod, "status": "erro", "mensagem": f"Provedor de IA retornou HTTP {he.code}"}
    except TimeoutError:
        return {"sucesso": False, "codigo": 504, "status": "erro", "mensagem": "Timeout na comunica\u00e7\u00e3o com o provedor de IA."}
    except urllib.error.URLError as ue:
        if isinstance(getattr(ue, "reason", None), TimeoutError):
            return {"sucesso": False, "codigo": 504, "status": "erro", "mensagem": "Timeout na comunica\u00e7\u00e3o com o provedor de IA."}
        return {"sucesso": False, "codigo": 502, "status": "erro", "mensagem": f"Falha de conex\u00e3o com o provedor de IA: {ue.reason}"}
    except Exception as e:
        return {"sucesso": False, "codigo": 502, "status": "erro", "mensagem": f"Erro ao processar resposta do provedor de IA: {e}"}

    if not isinstance(resp_dados, dict):
        return {"sucesso": False, "codigo": 502, "status": "erro", "mensagem": "Resposta inv\u00e1lida do provedor de IA (objeto JSON esperado)."}

    contexto_usuario = "\n".join(m["content"] for m in msgs_limpas if m["role"] in ("system", "user"))
    conteudo_resp = ""
    choices = resp_dados.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        msg_obj = choices[0].get("message")
        if isinstance(msg_obj, dict):
            conteudo_resp = str(msg_obj.get("content") or "")

    consistencia = verificar_consistencia_contextual(conteudo_resp, contexto_usuario)
    resp_dados["grounding"] = {
        "temperature_aplicada": temp_final,
        "max_tokens_aplicado": tokens_final,
        "consistencia": consistencia,
    }
    resp_dados["codigo"] = 200
    return resp_dados


def montar_contexto_processo(dados: Dict[str, Any]) -> str:
    campos = [
        ("Processo SEI", dados.get("idProcesso")),
        ("Especifica\u00e7\u00e3o / Objeto", dados.get("especificacao")),
        ("Tipo de Processo", dados.get("tipoProcesso")),
        ("Aging Bruto (dias)", dados.get("agingBruto")),
        ("Aging L\u00edquido (dias)", dados.get("agingLiquido")),
        ("Suspens\u00e3o / Por\u00e9m", dados.get("porem")),
        ("Farol de Criticidade", dados.get("farol")),
        ("Bucket OpenProject", dados.get("bucket")),
        ("Respons\u00e1vel T\u00e9cnico", dados.get("responsavel")),
        ("Card OpenProject", dados.get("cardId")),
    ]
    return "\n".join(f"- {rotulo}: {val}" for rotulo, val in campos if val not in (None, ""))


def revisar_processo_ia(
    dados: Dict[str, Any],
    endpoint: Optional[str] = None,
    model: str = "llama3.2:1b",
    api_key: str = "",
    timeout: int = 20,
    hosts_permitidos: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    if not isinstance(dados, dict) or not str(dados.get("idProcesso") or "").strip():
        return {"sucesso": False, "codigo": 400, "erro": "Campo obrigat\u00f3rio 'idProcesso' n\u00e3o informado."}

    contexto = montar_contexto_processo(dados)
    mensagens = [
        {
            "role": "system",
            "content": (
                "Voc\u00ea \u00e9 o assessor t\u00e9cnico de governan\u00e7a de TIC da SA-GTI (SP-\u00c1guas). "
                "Elabore um parecer t\u00e9cnico conciso, objetivo e em portugu\u00eas do Brasil sobre o processo abaixo."
            ),
        },
        {
            "role": "user",
            "content": (
                f"[CONTEXTO VERIFICADO DO PROCESSO]\n{contexto}\n\n"
                "Com base EXCLUSIVAMENTE nos dados acima, apresente: "
                "(1) s\u00edntese do status atual, (2) avalia\u00e7\u00e3o de criticidade/aging e eventual suspens\u00e3o (Por\u00e9m), "
                "e (3) recomenda\u00e7\u00e3o pr\u00e1tica para a SA-GTI."
            ),
        },
    ]

    res = executar_chat_ia(
        mensagens=mensagens,
        endpoint=endpoint,
        model=model,
        api_key=api_key,
        temperature=0.0,
        max_tokens=700,
        timeout=timeout,
        hosts_permitidos=hosts_permitidos,
    )

    if res.get("sucesso") is False:
        return {"sucesso": False, "codigo": res.get("codigo", 502), "erro": res.get("mensagem", "Falha ao gerar parecer pela IA.")}

    choices = res.get("choices") or []
    parecer = ""
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        msg_obj = choices[0].get("message")
        if isinstance(msg_obj, dict):
            parecer = str(msg_obj.get("content") or "").strip()

    if not parecer:
        return {"sucesso": False, "codigo": 502, "erro": "O provedor de IA retornou parecer vazio."}

    consistencia = (res.get("grounding") or {}).get("consistencia") or {"consistente": True, "alertas": []}
    if not consistencia.get("consistente"):
        return {
            "sucesso": False,
            "codigo": 422,
            "bloqueado_por_inconsistencia": True,
            "erro": "Parecer bloqueado por conter entidades fora do contexto verificado.",
            "consistencia": consistencia,
        }

    return {
        "sucesso": True,
        "codigo": 200,
        "parecer": parecer,
        "modelo": res.get("model") or model,
        "consistencia": consistencia,
    }
