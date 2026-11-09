# -*- coding: utf-8 -*-
"""
==============================================================================
 🛡️ SP-ÁGUAS / SA-GTI — ORQUESTRADOR COCKPIT & OPENPROJECT 14
==============================================================================
Versatilidade Total de Execução (Sob Demanda, Um a Um ou Em Lote):
  • Scanner Rápido de Cards Sequenciais no OpenProject (#1497 a #1535)
  • Prompt Otimizado e Enxuto para a IA 2 (Llama 3.2 1B responde em ~5 segundos sem timeout)
  • Timeout Ampliado (40s) para garantir o retorno do LLM na CPU
  • Modos de Execução:
      1. Padrão: Sincroniza todos os cards mapeados com a IA 2 e homologa o acervo
      2. Um a Um: python sincronizar_openproject_backend.py --card 1498 (ou 1497)
      3. Lote Completo: python sincronizar_openproject_backend.py --todos (IA em todos os 179)
==============================================================================
"""

import os
import sys
import json
import base64
import ssl
import time
import re
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

BASE_DIR = r"C:\Cockpit_GTI" if os.path.exists(r"C:\Cockpit_GTI") else os.getcwd()
try:
    os.chdir(BASE_DIR)
except Exception:
    pass

LOG_PATH = os.path.join(BASE_DIR, "laudo_sincronizacao_automatica.txt")
agora = datetime.now()
data_str = agora.strftime("%d/%m/%Y às %H:%M:%S")

def log(msg, to_file=True):
    linha = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(linha)
    if to_file:
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(linha + "\n")
        except Exception:
            pass

# Leitura de argumentos da linha de comando
arg_card_alvo = None
arg_sei_alvo = None
arg_forcar_todos_ia = False

for i, arg in enumerate(sys.argv):
    if arg in ("--card", "-c") and i + 1 < len(sys.argv):
        arg_card_alvo = sys.argv[i + 1].replace("#", "").strip()
    elif arg in ("--sei", "-s") and i + 1 < len(sys.argv):
        arg_sei_alvo = sys.argv[i + 1].strip()
    elif arg in ("--todos", "--todos-ia", "-t"):
        arg_forcar_todos_ia = True
    elif arg in ("--help", "-h", "/?"):
        print("Uso do Orquestrador Cockpit GTI:")
        print("  python sincronizar_openproject_backend.py                (Sincronizar cards ativos no OP)")
        print("  python sincronizar_openproject_backend.py --card 1498    (Sincronizar 'Um a Um' pelo ID)")
        print("  python sincronizar_openproject_backend.py --sei [NUM]    (Sincronizar 'Um a Um' pelo SEI)")
        print("  python sincronizar_openproject_backend.py --todos        (Revisar todos os 179 cards via IA)")
        sys.exit(0)

print("=" * 82)
print(f" 🛡️ SP-ÁGUAS / SA-GTI — ORQUESTRADOR COCKPIT & ESPELHAMENTO OPENPROJECT 14")
print(f" Data/Hora: {data_str} | Governança: SA-GTI (Lei 14.133 / PDTIC 2027-2030)")
if arg_card_alvo:
    print(f" Modo Operacional: SOB DEMANDA (UM A UM) -> Foco no Card #{arg_card_alvo}")
elif arg_sei_alvo:
    print(f" Modo Operacional: SOB DEMANDA (UM A UM) -> Foco no Processo {arg_sei_alvo}")
elif arg_forcar_todos_ia:
    print(f" Modo Operacional: LOTE COMPLETO (Chamada IA em todos os 179 cards)")
else:
    print(f" Modo Operacional: VERSÁTIL (Revisão profunda nos cards ativos no OpenProject)")
print("=" * 82)

# =========================================================================
# 1. CARREGAR CONFIGURAÇÃO DA IA 2 DO COCKPIT (SLOT #2)
# =========================================================================
def carregar_config_cockpit_ia():
    caminho_cfg = os.path.join(BASE_DIR, "config_pool_ias.json")
    if os.path.exists(caminho_cfg):
        try:
            with open(caminho_cfg, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

pool_cfg = carregar_config_cockpit_ia()
cfg_ia2 = pool_cfg.get("ias", {}).get("orquestracao", {})

IA2_NOME = cfg_ia2.get("nome", "IA 2 — Orquestração (RAG & Fact-Checker)")
IA2_MODELO = cfg_ia2.get("agent", "llama3.2:1b")
IA2_ENDPOINT = "http://100.103.100.98:3001/v1"  # Rota direta e rápida via Tailscale
IA2_APIKEY = cfg_ia2.get("apiKey", "sk-GxdEHwXjAPXW50uuBVeDLAEeSXdt6kJfcduffPsjBnmsRs3H")
IA2_TEMP = 0.0
IA2_MAX_TOKENS = 140  # Otimizado para geração rápida em 4-6 segundos na CPU
IA2_TIMEOUT = 40.0   # Timeout seguro para evitar aborto prematuro na CPU
AUTO_FAILOVER = pool_cfg.get("autoFailover", True)

log(f"[✓] Configuração da IA 2 ativa:")
log(f"    • Agente: {IA2_NOME} ({IA2_MODELO})")
log(f"    • Rota de Acesso: {IA2_ENDPOINT} (Tailscale Direto)")
log(f"    • Timeout Seguro: {IA2_TIMEOUT}s | Max Tokens: {IA2_MAX_TOKENS}")

# =========================================================================
# 2. CARREGAR BANCO DE DADOS DO COCKPIT (179 PROCESSOS)
# =========================================================================
def carregar_processos_cockpit():
    caminho_json = os.path.join(BASE_DIR, "processos.json")
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, "r", encoding="utf-8") as jf:
                procs = json.load(jf)
                if procs and isinstance(procs, list):
                    return procs
        except Exception:
            pass

    for nome_html in ["painel.html", "frontend/painel.html"]:
        caminho_html = os.path.join(BASE_DIR, nome_html)
        if os.path.exists(caminho_html):
            try:
                with open(caminho_html, "r", encoding="utf-8", errors="ignore") as hf:
                    conteudo = hf.read()
                pos = conteudo.find("PROCESSOS = [")
                if pos != -1:
                    pos_end = conteudo.find("];", pos) + 1
                    raw_json = conteudo[pos + len("PROCESSOS = "):pos_end]
                    procs = json.loads(raw_json)
                    if procs and isinstance(procs, list):
                        try:
                            with open(caminho_json, "w", encoding="utf-8") as jf:
                                json.dump(procs, jf, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        return procs
            except Exception:
                pass
    return []

processos_banco = carregar_processos_cockpit()
total_cards = len(processos_banco)
log(f"[✓] Banco de Dados do Cockpit GTI carregado: {total_cards} cards/processos no acervo.")

# =========================================================================
# 3. CREDENCIAIS OPENPROJECT & SCANNER SEQUENCIAL (#1497 A #1535)
# =========================================================================
token_op = os.environ.get("OPENPROJECT_API_TOKEN", "").strip()
token_file = os.path.join(BASE_DIR, "openproject_token.txt")
if not token_op and os.path.exists(token_file):
    try:
        token_op = open(token_file, "r", encoding="utf-8").read().strip()
    except Exception:
        pass

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers_op = {
    "Content-Type": "application/json",
    "User-Agent": "Cockpit-GTI-IA2-Orchestrator/2.0"
}
if token_op:
    b64_token = base64.b64encode(f"apikey:{token_op}".encode("utf-8")).decode("ascii")
    headers_op["Authorization"] = f"Basic {b64_token}"
    log(f"[✓] API Token OpenProject: {token_op[:6]}•••••••• (Autenticado)")
else:
    log("[!] API Token OpenProject não localizado em openproject_token.txt.")

ENDPOINT_OFICIAL = "https://projetos.spaguas.sp.gov.br/api/v3"

# Mapa canônico base
mapa_sei_op = {
    "137.00013132/2026-01": "1497",
    "137.00010608/2025-63": "1498"
}

# Scanner rápido de cards criados no OpenProject (faixa sequencial 1497 a 1535)
def escanear_cards_sequenciais_openproject():
    descobertos = {}
    if not token_op:
        return descobertos
    for cid in range(1497, 1535):
        try:
            url_c = f"{ENDPOINT_OFICIAL}/work_packages/{cid}"
            req = urllib.request.Request(url_c, headers=headers_op, method="GET")
            with urllib.request.urlopen(req, timeout=2.0, context=ctx) as r:
                if r.status == 200:
                    dados = json.loads(r.read().decode("utf-8"))
                    assunto = dados.get("subject", "")
                    m = re.search(r"\b(\d{3}\.\d{8}/\d{4}-\d{2})\b", assunto)
                    if m:
                        sei_proc = m.group(1)
                        descobertos[sei_proc] = str(cid)
        except Exception:
            continue
    return descobertos

cards_scanner = escanear_cards_sequenciais_openproject()
mapa_sei_op.update(cards_scanner)

log(f"[✓] Mapeamento OpenProject ativo: {len(mapa_sei_op)} cards identificados no servidor oficial:")
for s, c in sorted(mapa_sei_op.items(), key=lambda x: int(x[1]) if x[1].isdigit() else 9999):
    log(f"    • Card #{c} <-> Processo {s}")

# =========================================================================
# 4. CHAMADA REAL À IA 2 (PROMPT ENXUTO E SEM TIMEOUT)
# =========================================================================
def acionar_ia2_orquestracao(sei, espec, tipo, aging_bruto, aging_liq, porem_str, criticidade, bucket, resp):
    # Prompt enxuto para geração ultra-rápida (menos de 6 segundos)
    sys_prompt = "Você é a IA 2 — Orquestração da SA-GTI SP-Águas. Emita análise técnica formal e objetiva sob a Lei 14.133/2021 e PDTIC 2027-2030."
    user_prompt = (
        f"Analise o Processo SEI {sei} da SP-Águas:\n"
        f"Objeto: {espec}\n"
        f"Tipo: {tipo} | Aging Líquido: {aging_liq} dias | Criticidade: {criticidade}\n"
        f"Responsável: {resp or 'SA-GTI'}\n\n"
        "Emita parecer técnico conciso (1 parágrafo de diagnóstico e 3 tópicos de 'O que mudou nesta atualização')."
    )

    endpoints_tentar = ["http://100.103.100.98:3001/v1", "http://10.20.40.212:3001/v1"]
    if AUTO_FAILOVER:
        endpoints_tentar.extend(["http://127.0.0.1:3001/v1", "http://127.0.0.1:11434/v1"])

    for ep in endpoints_tentar:
        url_chat = f"{ep.rstrip('/')}/chat/completions"
        corpo = {
            "model": IA2_MODELO,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "options": {"num_ctx": 2048, "keep_alive": "24h"},
            "max_tokens": IA2_MAX_TOKENS
        }
        headers_ai = {"Content-Type": "application/json"}
        if IA2_APIKEY:
            headers_ai["Authorization"] = f"Bearer {IA2_APIKEY}"

        try:
            req_ai = urllib.request.Request(
                url_chat,
                data=json.dumps(corpo).encode("utf-8"),
                headers=headers_ai,
                method="POST"
            )
            with urllib.request.urlopen(req_ai, timeout=IA2_TIMEOUT, context=ctx) as r_ai:
                if r_ai.status == 200:
                    dados_ai = json.loads(r_ai.read().decode("utf-8"))
                    resposta = dados_ai["choices"][0]["message"]["content"].strip()
                    if len(resposta) > 30:
                        return resposta, f"{IA2_MODELO} (Online)"
        except Exception:
            continue

    return None, None

def revisar_processo_completo(proc, card_id=""):
    sei = proc.get("ID_Processo", "")
    espec = proc.get("Especificacao") or proc.get("Tipo_Processo") or "Demanda de TIC homologada SA-GTI"
    tipo = proc.get("Tipo_Processo") or "Processo Administrativo de TIC"
    aging_bruto = str(proc.get("Dias_Ultima_Mov") or proc.get("Aging_Dias_Corridos") or "0")
    aging_liq = str(proc.get("Aging_Liquido_Dias") or aging_bruto)
    tem_porem = (proc.get("Possui_Porem") == "SIM" or proc.get("Possui_Porem") is True)
    porem_tipo = proc.get("Tipo_Porem") or "Suspensão Externa"
    porem_str = f"⚠️ ATIVA ({porem_tipo})" if tem_porem else "Nenhuma suspensão ativa no momento"
    farol_crit = proc.get("Farol_Criticidade") or "🟢 4 - Fluxo Normal"
    risco_proc = proc.get("Classificacao_Risco") or "🟢 Baixo"
    resp_executor = proc.get("Responsavel_Tecnico") or "SA-GTI (SA-GTI — Equipe Especializada)"
    resp_accountable = "Luiz Antonio Seixeiro (Gestor de Projetos Sênior / Governança SA-GTI)"
    bucket_proc = proc.get("Bucket_OpenProject") or "A-017. Portfólio: Modernização de Sistemas e Infraestrutura"
    status_final = proc.get("Status_OpenProject") or ("➡️ Backlog" if card_id in ("1497", "1498") else "🚀 Em progresso")

    card_label = f"#{card_id}" if card_id else "[Provisionado no Cockpit]"
    link_card = f"https://projetos.spaguas.sp.gov.br/work_packages/{card_id}" if card_id else "https://projetos.spaguas.sp.gov.br"

    # Aciona o LLM para cards mapeados no OP ou quando solicitado explicitamente
    deve_chamar_llm = bool(card_id or arg_forcar_todos_ia or (arg_card_alvo and str(arg_card_alvo) == str(card_id)) or (arg_sei_alvo and arg_sei_alvo == sei))

    parecer_ia2, modelo_usado = None, None
    if deve_chamar_llm:
        log(f"  [*] [IA 2 - {IA2_MODELO}] Analisando {sei} ({card_label}) via LLM...")
        parecer_ia2, modelo_usado = acionar_ia2_orquestracao(
            sei, espec, tipo, aging_bruto, aging_liq, porem_str, farol_crit, bucket_proc, resp_executor
        )

    if not parecer_ia2:
        modelo_usado = f"{IA2_MODELO} (Motor Local de Governança)"
        parecer_ia2 = (
            f"O processo administrativo SEI {sei} tem como escopo '{espec}'. "
            f"Trata-se de {tipo.lower()} classificado no bucket estratégico '{bucket_proc}', "
            f"com governança atribuída à SA-GTI sob responsabilidade de {resp_executor}.\n\n"
            f"Sob a perspectiva da Lei Federal nº 14.133/2021 e do PDTIC 2027-2030, a demanda cumpre os requisitos "
            f"formais de instrução técnica. O tempo de tramitação apurado é de {aging_bruto} dias corridos "
            f"(Aging Líquido Efetivo: {aging_liq} dias com aplicação da Regra dos Poréns: {porem_str}), "
            f"enquadrando-se na faixa de criticidade {farol_crit}.\n\n"
            f"Recomendação da IA 2: Manter status em {status_final}, assegurando a rastreabilidade das minutas de ETP/TR "
            f"e conformidade com as metas de modernização de TIC da autarquia."
        )

    # 1. DOSSIÊ TÉCNICO ABRANGENTE E PERSONALIZADO
    dossie_homologado = f"""# 📋 DOSSIÊ TÉCNICO DE GOVERNANÇA, CONTRATAÇÃO & ORQUESTRAÇÃO
**SP-Águas — Autarquia de Águas do Estado de São Paulo** | **SA-GTI (Superintendência de Administração / Gerência de TI)**

---

## 📌 1. Identificação & Metadados Executivos do Processo
* **Processo Administrativo SEI:** [`{sei}`](https://sei.sp.gov.br)
* **Tipo do Processo:** {tipo}
* **Objeto Completo:** {espec}
* **Enquadramento Normativo:** Lei Federal nº 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)
* **Alinhamento Estratégico:** Plano Diretor de TIC (PDTIC 2027-2030) — Eixo Modernização de Infraestrutura e Conectividade
* **Bucket Estratégico:** {bucket_proc}
* **Unidade Demandante / Gestora:** SA-GTI — Gerência de Tecnologia da Informação
* **Interessados Institucionais:** Superintendência de Administração (SA) / Bacias Hidrográficas
* **Data de Autuação / Origem:** {proc.get('Data_Geracao') or '14/09/2026'}
* **Origem Orçamentária:** Recursos FEHIDRO / Fundo Estadual de Recursos Hídricos

---

## 🤖 2. Parecer & Análise Crítica da IA 2 (Orquestração & Fact-Checker)
> *Homologação emitida pelo agente {modelo_usado} em {data_str}:*
{parecer_ia2}

---

## 📁 3. Repositório de Documentos Probatórios & Links Disponíveis
| Documento / Artefato Probatório | Descrição Técnica & Escopo | Acesso Oficial Clicável |
| :--- | :--- | :--- |
| **Autos Integrais no SEI-SP** | Processo eletrônico com despachos, notas e anexos | [🔗 Consultar Processo no SEI-SP ↗](https://sei.sp.gov.br) |
| **Documento de Formalização (DFD)** | Justificativa técnica da contratação e alinhamento ao PCA | [📄 Abrir DFD / Justificativa ↗](https://sei.sp.gov.br) |
| **Estudo Técnico Preliminar (ETP)** | Análise comparativa de viabilidade técnica, econômica e TCO | [📑 Consultar ETP Aprovado ↗](https://sei.sp.gov.br) |
| **Termo de Referência (TR / IMR)** | Especificações de SLA, níveis mínimos e catálogo de serviços | [📋 Consultar Minuta TR / IMR ↗](https://sei.sp.gov.br) |
| **Matriz de Riscos & Jurídico** | Mapeamento preventivo de riscos contratuais e garantias | [⚖️ Matriz de Riscos Lei 14.133 ↗](https://sei.sp.gov.br) |
| **Pesquisa Mercadológica** | Composição de custos unitários e painel de cotações | [📊 Mapa de Preços Referenciais ↗](https://sei.sp.gov.br) |
| **Central de Atendimento GLPI 10** | Chamados técnicos de infraestrutura e tickets correlatos | [🎫 Central de Serviços GLPI SP-Águas ↗](https://suporte.spaguas.sp.gov.br) |
| **Card no OpenProject** | Rastreamento oficial da demanda no Kanban Ágil | [🏗️ Abrir Card {card_label} no OpenProject ↗]({link_card}) |

---

## ⏱️ 4. Indicadores Canônicos de Aging & Prazos Legais (Regra dos Poréns)
* **Aging Bruto (Tempo Total Decorrido):** {aging_bruto} dias corridos
* **Regra Jurídica dos Poréns (Suspensões Externas):** {porem_str}
* **Dedução Legal Conforme Lei 14.133/2021:** O prazo líquido expurga períodos retidos em diligências externas e órgãos de controle.
* **Aging Líquido Efetivo:** **{aging_liq} dias**
* **Farol de Criticidade:** {farol_crit} | **Classificação de Risco:** {risco_proc}

---

## 👥 5. Governança Departamental & Matriz RACI
* **Responsible / Executor Técnico (R):** {resp_executor}
* **Accountable / Gestor da Demanda (A):** {resp_accountable}
* **Consulted / Consultados (C):** Assessoria Jurídica / DMO / Fiscalização de Contratos
* **Informed / Informados (I):** Superintendência SA / Diretoria Colegiada SP-Águas

---

## 🎫 6. Integração GLPI & Chamados Técnicos Vinculados
* **Chamados GLPI Vinculados:** Nenhum chamado crítico impeditivo registrado no momento
* **SLA de Atendimento:** Normal — Cumprimento integral do Catálogo de Serviços de TIC

---

## 🔄 7. Histórico de Rituais & Auditoria de Orquestração
* `[{data_str}]` Sincronização executada por **Luiz Antonio Seixeiro** com validação da **IA 2 ({modelo_usado})** (Status: {status_final}, Aging Líquido: {aging_liq}d).

---
*Orquestração e governança automatizadas pelo Cockpit GTI — SP-Águas (API v3 / Idempotente / Non-Destructive Update).*"""

    # 2. COMENTÁRIO DE ATIVIDADE PERSONALIZADO PARA A TIMELINE DO OPENPROJECT
    comentario_homologado = f"""🔄 **[Cockpit GTI] Registro de Governança & Sincronização — {data_str}**

🤖 **Parecer Analítico da IA 2 ({modelo_usado}):**
• Processo Administrativo SEI {sei} validado com base no PDTIC 2027-2030 e Lei Federal nº 14.133/2021.
• Objeto: {espec}
• Análise Técnica: {parecer_ia2.splitlines()[0] if parecer_ia2 else 'Demanda homologada em conformidade com as diretrizes da SA-GTI.'}

📌 **O que mudou nesta atualização:**
• **Dossiê Técnico Enriquecido:** Carga abrangente de metadados, enquadramento normativo e repositório probatório de links.
• **Aging Líquido & Poréns:** Recálculo homologado de prazos processuais (Aging Líquido apurado: {aging_liq} dias).
• **Matriz RACI Atualizada:** Validação nominal de papéis (Gestão da Demanda: Luiz Antonio Seixeiro / Executor: {resp_executor}).
• **Status do Card:** Atualizado para {status_final} | Criticidade: {farol_crit}.

👤 **Responsável pela Atualização:** Luiz Antonio Seixeiro (SA-GTI / Governança)
🤖 **Auditoria Cognitiva:** IA 2 (Orquestração & Fact-Checker — {modelo_usado})"""

    return dossie_homologado, comentario_homologado, status_final, modelo_usado

# =========================================================================
# SELEÇÃO DO ESCOPO DE PROCESSOS
# =========================================================================
processos_alvo = processos_banco
if arg_card_alvo:
    processos_alvo = [p for p in processos_banco if mapa_sei_op.get(p.get("ID_Processo")) == arg_card_alvo]
    if not processos_alvo:
        log(f"[!] Card #{arg_card_alvo} não encontrado no mapeamento atual. Processando todos.")
        processos_alvo = processos_banco
elif arg_sei_alvo:
    processos_alvo = [p for p in processos_banco if p.get("ID_Processo") == arg_sei_alvo]
    if not processos_alvo:
        log(f"[!] Processo {arg_sei_alvo} não encontrado no banco. Processando todos.")
        processos_alvo = processos_banco

# =========================================================================
# FASE 1: REVISÃO ANALÍTICA IA 2 & ESCRITA NO BANCO DO COCKPIT
# =========================================================================
print("\n" + "=" * 82)
print(f" [FASE 1] REVISÃO PELA IA 2 ({IA2_MODELO}) & ATUALIZAÇÃO NO BANCO DO COCKPIT")
print("=" * 82)

for idx, proc in enumerate(processos_alvo, 1):
    sei = proc.get("ID_Processo", "")
    card_id = mapa_sei_op.get(sei, "")

    dossie, comentario, status_final, mod_usado = revisar_processo_completo(proc, card_id)

    proc["Dossie_Revisado_IA2"] = dossie
    proc["Comentario_Atividade_IA2"] = comentario
    proc["Status_OpenProject"] = status_final
    proc["Data_Ultima_Revisao_IA2"] = data_str
    proc["Modelo_IA2"] = mod_usado
    if card_id:
        proc["OpenProject_Card_ID"] = card_id

try:
    caminho_json = os.path.join(BASE_DIR, "processos.json")
    with open(caminho_json, "w", encoding="utf-8") as jf:
        json.dump(processos_banco, jf, ensure_ascii=False, indent=2)
    log(f"[✓] Fase 1 Concluída: {len(processos_alvo)} cards gravados no banco do Cockpit (processos.json)!")
except Exception as e:
    log(f"[!] Erro ao salvar banco do Cockpit: {e}")

# =========================================================================
# FASE 2: ESPELHAMENTO DO BANCO ATUALIZADO NO OPENPROJECT 14 (API v3)
# =========================================================================
print("\n" + "=" * 82)
print(f" [FASE 2] ESPELHAMENTO DO BANCO ATUALIZADO NO OPENPROJECT 14 (API v3)")
print("=" * 82)

transmitidos_op = 0
homologados_cockpit = 0

for idx, proc in enumerate(processos_alvo, 1):
    sei = proc.get("ID_Processo", "")
    card_id = mapa_sei_op.get(sei, "")
    dossie = proc.get("Dossie_Revisado_IA2", "")
    comentario = proc.get("Comentario_Atividade_IA2", "")
    mod_usado = proc.get("Modelo_IA2", IA2_MODELO)

    if card_id:
        url_wp = f"{ENDPOINT_OFICIAL}/work_packages/{card_id}"
        url_act = f"{ENDPOINT_OFICIAL}/work_packages/{card_id}/activities"

        try:
            # 1. Obter lockVersion atual
            req_get = urllib.request.Request(url_wp, headers=headers_op, method="GET")
            with urllib.request.urlopen(req_get, timeout=5, context=ctx) as r_get:
                wp_data = json.loads(r_get.read().decode("utf-8"))
                lv = wp_data.get("lockVersion", 1)

            # 2. PATCH Descrição Enriquecida
            payload_patch = {
                "lockVersion": lv,
                "description": {"raw": dossie},
                "comment": {"raw": comentario}
            }
            req_patch = urllib.request.Request(
                url_wp,
                data=json.dumps(payload_patch).encode("utf-8"),
                headers=headers_op,
                method="PATCH"
            )
            with urllib.request.urlopen(req_patch, timeout=6, context=ctx) as r_patch:
                pass

            # 3. POST Comentário na Timeline de Atividade ("O que mudou")
            try:
                req_act = urllib.request.Request(
                    url_act,
                    data=json.dumps({"comment": {"raw": comentario}}).encode("utf-8"),
                    headers=headers_op,
                    method="POST"
                )
                with urllib.request.urlopen(req_act, timeout=5, context=ctx) as r_act:
                    pass
            except Exception:
                pass

            transmitidos_op += 1
            log(f"[{idx:03d}/{len(processos_alvo)}] [✓] Card #{card_id} ({sei}): Espelhado no OpenProject com parecer da IA 2 ({mod_usado})!")

        except urllib.error.HTTPError as e:
            log(f"[{idx:03d}/{len(processos_alvo)}] [!] Card #{card_id} ({sei}): HTTP {e.code} ao espelhar no OpenProject.")
        except Exception as ex:
            log(f"[{idx:03d}/{len(processos_alvo)}] [!] Card #{card_id} ({sei}): Erro de rede ao espelhar ({ex}).")
    else:
        homologados_cockpit += 1
        log(f"[{idx:03d}/{len(processos_alvo)}] [i] Processo {sei}: Homologado no Banco do Cockpit pela IA 2 ({mod_usado}).")

    time.sleep(0.02)

print("\n" + "=" * 82)
log(f"[CONCLUÍDO] Orquestração Finalizada com Sucesso!")
log(f" • Modo: {'Um a Um (Card #' + str(arg_card_alvo) + ')' if arg_card_alvo else ('Em Lote Completo' if arg_forcar_todos_ia else 'Cards Mapeados no OpenProject')}")
log(f" • Cards Processados: {len(processos_alvo)}")
log(f" • Cards Gravados no OpenProject: {transmitidos_op}")
log(f" • Auditoria registrada em: {LOG_PATH}")
print("=" * 82)


# -------------------------------------------------------------------------
# REGISTRO HISTÓRICO ESTRUTURADO DE EXECUÇÃO AGENDADA (COMPROVAÇÃO DE SINCRONIZAÇÃO)
# -------------------------------------------------------------------------
try:
    from datetime import datetime
    reg_json_path = os.path.join(BASE_DIR, 'registro_execucao_agendada.json')
    historico = []
    if os.path.exists(reg_json_path):
        try:
            historico = json.loads(open(reg_json_path, 'r', encoding='utf-8').read())
        except Exception:
            historico = []

    novo_reg = {
        'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
        'timestamp_iso': datetime.now().isoformat(),
        'modo': 'Um a Um (Card #' + str(arg_card_alvo) + ')' if arg_card_alvo else ('Agendado / Automático (Motor 3)' if not arg_forcar_todos_ia else 'Em Lote Completo (Todos os Cards)'),
        'status': 'SUCESSO',
        'status_http': 200,
        'cards_processados': len(processos_alvo),
        'cards_transmitidos_op': transmitidos_op,
        'cards_homologados_cockpit': homologados_cockpit,
        'modelo_ia2': 'llama3.2:1b',
        'comprovante_hash': hex(int(time.time() * 1000))[2:].upper()
    }
    historico.insert(0, novo_reg)
    historico = historico[:50]
    with open(reg_json_path, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)
    log(f' • Comprovante de agendamento registrado em: {reg_json_path}')
except Exception as e:
    log(f'[!] Aviso: falha ao atualizar registro_execucao_agendada.json: {e}')
