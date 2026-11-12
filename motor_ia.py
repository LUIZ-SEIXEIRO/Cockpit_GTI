# -*- coding: utf-8 -*-
import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List
from urllib.parse import urlparse

RE_PROCESSO_SEI = re.compile(r"\b\d{3}\.\d{8}/\d{4}-\d{2}\b")

DIRETRIZ_GROUNDING_ESTRIRO = (
    "[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]\n"
    "1. Responda EXCLUSIVAMENTE com base nos dados verificados presentes no contexto desta conversa.\n"
    "2. Se uma informa\u00e7\u00e3o (n\u00famero de processo SEI, prazo, valor, norma ou respons\u00e1vel) n\u00e3o constar no contexto, "
    "declare explicitamente: 'Informa\u00e7\u00e3o n\u00e3o localizada no contexto fornecido.'\n"
    "3. Nunca invente n\u00fameros de processo, datas, m\u00e9tricas ou cita\u00e7\u00f5es legais."
)


def normalizar_temperatura(valor: Any, padrao: float = 0.0) -> float:
    if valor is None or valor == "":
        t = padrao
    else:
        try:
            t = float(valor)
        except (TypeError, ValueError):
            t = padrao
    if t < 0.0:
        return 0.0
    if t > 0.7:
        return 0.7
    return round(t, 4)


def normalizar_max_tokens(valor: Any, padrao: int = 700) -> int:
    if valor is None or valor == "":
        n = padrao
    else:
        try:
            n = int(valor)
        except (TypeError, ValueError):
            n = padrao
    if n < 64:
        return 64
    if n > 4096:
        return 4096
    return n


def validar_endpoint_ia(endpoint: str) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("Endpoint de IA n\u00e3o informado.")
    limpo = endpoint.strip().rstrip("/")
    parsed = urlparse(limpo)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Endpoint de IA inv\u00e1lido: {endpoint}")
    return limpo


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
    resultado = [dict(m) for m in mensagens]
    for msg in resultado:
        if msg["role"] == "system":
            if "[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]" not in msg["content"]:
                msg["content"] = msg["content"].rstrip() + "\n\n" + DIRETRIZ_GROUNDING_ESTRIRO
            return resultado
    return [{"role": "system", "content": DIRETRIZ_GROUNDING_ESTRIRO}] + resultado


def avaliar_fidelidade_resposta(resposta: str, contexto: str) -> Dict[str, Any]:
    texto_resp = str(resposta or "").strip()
    texto_ctx = str(contexto or "")
    alertas: List[str] = []

    if not texto_resp:
        return {"fiel": False, "score": 0.0, "alertas": ["Resposta vazia."]}

    procs_ctx = set(RE_PROCESSO_SEI.findall(texto_ctx))
    procs_resp = set(RE_PROCESSO_SEI.findall(texto_resp))
    alucinados = sorted(procs_resp - procs_ctx)
    if alucinados:
        alertas.append(
            f"N\u00famero(s) de processo SEI citado(s) fora do contexto: {', '.join(alucinados)}"
        )

    score = 1.0 if not alertas else max(0.0, round(1.0 - 0.5 * len(alertas), 2))
    return {"fiel": len(alertas) == 0, "score": score, "alertas": alertas}


def executar_chat_ia(
    mensagens: Any,
    endpoint: str = "http://127.0.0.1:3001/v1",
    model: str = "qwen2.5:14b",
    api_key: str = "",
    temperature: Any = 0.0,
    max_tokens: Any = 700,
    timeout: int = 45,
) -> Dict[str, Any]:
    try:
        endpoint_valido = validar_endpoint_ia(endpoint)
        msgs_limpas = sanitizar_mensagens(mensagens)
    except ValueError as e:
        return {"sucesso": False, "codigo": 400, "status": "erro", "mensagem": str(e)}

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

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers_req,
        method="POST",
    )

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

    contexto_usuario = "\n".join(m["content"] for m in msgs_limpas if m["role"] in ("system", "user"))
    conteudo_resp = ""
    choices = resp_dados.get("choices")
    if isinstance(choices, list) and choices:
        conteudo_resp = str(((choices[0] or {}).get("message") or {}).get("content") or "")

    fidelidade = avaliar_fidelidade_resposta(conteudo_resp, contexto_usuario)
    resp_dados["grounding"] = {
        "temperature_aplicada": temp_final,
        "max_tokens_aplicado": tokens_final,
        "fidelidade": fidelidade,
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
    linhas = [f"- {rotulo}: {val}" for rotulo, val in campos if val not in (None, "")]
    return "\n".join(linhas)


def revisar_processo_ia(
    dados: Dict[str, Any],
    endpoint: str = "http://127.0.0.1:3001/v1",
    model: str = "llama3.2:1b",
    api_key: str = "",
    timeout: int = 20,
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
    )

    if res.get("sucesso") is False:
        return {"sucesso": False, "codigo": res.get("codigo", 502), "erro": res.get("mensagem", "Falha ao gerar parecer pela IA.")}

    choices = res.get("choices") or []
    parecer = ""
    if choices and isinstance(choices[0], dict):
        parecer = str(((choices[0].get("message") or {}).get("content")) or "").strip()

    if not parecer:
        return {"sucesso": False, "codigo": 502, "erro": "O provedor de IA retornou parecer vazio."}

    return {
        "sucesso": True,
        "codigo": 200,
        "parecer": parecer,
        "modelo": res.get("model") or model,
        "fidelidade": (res.get("grounding") or {}).get("fidelidade"),
    }
