# -*- coding: utf-8 -*-
import os, re

paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]

nova_padrao = """MOTORES_PADRAO = [
        {
                "id": "mot-1",
                "nome": "1. 🗄️ MariaDB 10.11 (SSOT :3306 glpidb)",
                "tipo": "SQL / Relacional",
                "endpoint": "http://localhost:5000/api/v1/mariadb/status",
                "endpoint_remoto": "127.0.0.1:3306",
                "freq": "Tempo Real",
                "status": "ativo",
                "modo_resiliencia": "fonte_local_ssot",
                "desc": "Banco de Dados Canônico da autarquia (179 Autos SEI, RBAC e Feeds de TI)"
        },
        {
                "id": "mot-2",
                "nome": "2. 🤖 Gateway New API (:3001) / Ollama (:11434)",
                "tipo": "REST API / OpenAI",
                "endpoint": "http://localhost:3001/v1/models",
                "endpoint_remoto": "http://localhost:3001/v1/models",
                "freq": "A cada 15 min",
                "status": "ativo",
                "modo_resiliencia": "pool_3_ias_failover",
                "desc": "Gateway central de modelos LLM (Gemini Nuvem / Modelos Locais Ollama)"
        },
        {
                "id": "mot-3",
                "nome": "3. 🏗️ OpenProject 14 Produção (API v3 :8090)",
                "tipo": "OpenProject API v3",
                "endpoint": "http://localhost:8090/api/v3",
                "endpoint_remoto": "http://localhost:8090/api/v3",
                "freq": "A cada 15 min",
                "status": "ativo",
                "modo_resiliencia": "snapshot_500_pacotes",
                "desc": "Sincronização de 500 Work Packages em 29 Projetos e rituais ágeis"
        },
        {
                "id": "mot-4",
                "nome": "4. 🎫 GLPI 10 ITSM & Formcreator (:8088)",
                "tipo": "REST API Local",
                "endpoint": "http://localhost:8088/apirest.php",
                "endpoint_remoto": "http://localhost:8088/apirest.php",
                "freq": "A cada 30 min",
                "status": "ativo",
                "modo_resiliencia": "base_203_chamados",
                "desc": "Tickets de suporte N1/N2/N3 (24 ITSM TI + 179 demandas SEI) e CMDB"
        },
        {
                "id": "mot-5",
                "nome": "5. 📡 Sonda Zabbix NOC (Telemetria Bacias)",
                "tipo": "JSON-RPC / REST Proxy",
                "endpoint": "http://localhost:5000/api/v1/zabbix/status",
                "endpoint_remoto": "http://localhost:8098/zabbix/api_jsonrpc.php",
                "freq": "A cada 15 min",
                "status": "ativo",
                "modo_resiliencia": "telemetria_22_ugrhis",
                "desc": "Monitoramento de disponibilidade de links WAN/SD-WAN nas 22 UGRHIs"
        },
        {
                "id": "mot-6",
                "nome": "6. 📂 Robô Ingestão SEI v7.1 (ETL de PDFs)",
                "tipo": "ETL Autônomo / Python",
                "endpoint": "http://localhost:5000/api/v1/sei/status",
                "endpoint_remoto": "http://localhost:5000/api/v1/sei/status",
                "freq": "A cada 30 min",
                "status": "ativo",
                "modo_resiliencia": "processamento_manual_v71",
                "desc": "Processamento e ingestão contínua de relatórios oficiais do SEI e Poréns"
        },
        {
                "id": "mot-7",
                "nome": "7. 🏛️ Acervo & Diário Oficial (DOE-SP)",
                "tipo": "HTTPS / Web Oficial",
                "endpoint": "https://www.doe.sp.gov.br",
                "endpoint_remoto": "https://www.doe.sp.gov.br",
                "freq": "A cada 60 min",
                "status": "ativo",
                "modo_resiliencia": "sonda_https_anticors",
                "desc": "Varredura de deliberações, portarias e contratos publicados no DOE-SP"
        },
        {
                "id": "mot-8",
                "nome": "8. 📑 API Oficial PNCP (UASG 262101 • PCA 2027)",
                "tipo": "REST API / PNCP",
                "endpoint": "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260101&dataFinal=20261231&codigoUnidadeAdministrativa=262101&pagina=1&tamanhoPagina=1",
                "endpoint_remoto": "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao",
                "freq": "A cada 60 min",
                "status": "ativo",
                "modo_resiliencia": "espelho_uasg_262101",
                "desc": "Conciliação orçamentária de contratações de TIC com LOA e PNCP (UASG 262101)"
        },
        {
                "id": "mot-9",
                "nome": "9. 💧 Barramento Hídrico SIGRH / SOI / SOE",
                "tipo": "REST API Proxy",
                "endpoint": "http://localhost:5000/api/v1/soi/status",
                "endpoint_remoto": "http://sigrh.sp.gov.br/api/v1/demandas",
                "freq": "A cada 60 min",
                "status": "ativo",
                "modo_resiliencia": "espelho_demandas_hidricas",
                "desc": "Mapeamento de outorgas, poços tubulares e telemetria hídrica da DMO"
        },
        {
                "id": "mot-10",
                "nome": "10. ⚖️ Tribunal de Contas do Estado (TCE-SP)",
                "tipo": "Web Scraper / Consulta",
                "endpoint": "https://www.tce.sp.gov.br",
                "endpoint_remoto": "https://www.tce.sp.gov.br",
                "freq": "A cada 60 min",
                "status": "ativo",
                "modo_resiliencia": "jurisprudencia_sumula_269",
                "desc": "Jurisprudência, Súmula 269 TCU e auditoria de conformidade legal de TIC"
        },
        {
                "id": "mot-11",
                "nome": "11. 🌊 Portal Institucional SP-Águas & Regimento",
                "tipo": "HTTPS Oficial",
                "endpoint": "https://www.spaguas.sp.gov.br",
                "endpoint_remoto": "https://www.spaguas.sp.gov.br",
                "freq": "A cada 60 min",
                "status": "ativo",
                "modo_resiliencia": "deliberacao_21_decretos",
                "desc": "Indexação Regimental da Deliberação nº 21/2026, decretos estaduais e portarias"
        }
];"""

nova_canonicos = """window.MOTORES_CANONICOS_V9 = [
        { id: 'mariadb_ssot', nome: '1. 🗄️ MariaDB 10.11 (SSOT :3306 glpidb)', endpoint: 'http://localhost:5000/api/v1/mariadb/status', fallbackTipo: 'fonte_local', detalheLocal: 'Banco de Dados Canônico (179 Autos SEI + Usuários RBAC)' },
        { id: 'newapi_gateway', nome: '2. 🤖 Gateway New API (:3001) / Ollama (:11434)', endpoint: 'http://localhost:3001/v1/models', fallbackTipo: 'fonte_local', detalheLocal: 'Pool Multi-IA com Failover (Gemini Nuvem / Modelos Locais)' },
        { id: 'openproject_14', nome: '3. 🏗️ OpenProject Produção API v3 (:8090)', endpoint: 'http://localhost:8090/api/v3', fallbackTipo: 'fonte_local', detalheLocal: 'Snapshot Oficial com 500 Pacotes Reais em 29 Projetos' },
        { id: 'glpi_10', nome: '4. 🎫 GLPI 10 ITSM & Formcreator (:8088)', endpoint: 'http://localhost:8088/apirest.php', fallbackTipo: 'fonte_local', detalheLocal: 'Base Auditada com 203 Chamados (24 ITSM + 179 Demandas SEI)' },
        { id: 'zabbix_noc', nome: '5. 📡 Sonda Zabbix NOC (Telemetria Bacias)', endpoint: 'http://localhost:5000/api/v1/zabbix/status', fallbackTipo: 'fonte_local', detalheLocal: 'Monitoramento de SLA WAN/SD-WAN nas 22 UGRHIs' },
        { id: 'sei_pdf_etl', nome: '6. 📂 Robô Ingestão SEI v7.1 (ETL de PDFs)', endpoint: 'http://localhost:5000/api/v1/sei/status', fallbackTipo: 'fonte_local', detalheLocal: 'Processamento e Ingestão de Relatórios SEI (Manual v7.1)' },
        { id: 'doe_sp', nome: '7. 🏛️ Acervo & Diário Oficial (DOE-SP)', endpoint: 'https://www.doe.sp.gov.br', fallbackTipo: 'online_doesp', detalheLocal: 'Conectado a https://www.doe.sp.gov.br (Sonda HTTPS Anti-CORS)' },
        { id: 'pncp_pca', nome: '8. 📑 API Oficial PNCP (UASG 262101 • PCA 2027)', endpoint: 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260101&dataFinal=20261231&codigoUnidadeAdministrativa=262101&pagina=1&tamanhoPagina=1', fallbackTipo: 'fonte_local', detalheLocal: 'Espelho Auditado UASG 262101 (31 Pacotes PCA 2027 • R$ 1,51 bi)' },
        { id: 'soi_soe', nome: '9. 💧 Barramento Hídrico SIGRH / SOI / SOE', endpoint: 'http://localhost:5000/api/v1/soi/status', fallbackTipo: 'fonte_local', detalheLocal: 'Sistemas de Outorga de Água, Poços e Telemetria DMO' },
        { id: 'tce_sp', nome: '10. ⚖️ Tribunal de Contas do Estado (TCE-SP)', endpoint: 'https://www.tce.sp.gov.br', fallbackTipo: 'fonte_local', detalheLocal: 'Jurisprudência, Súmula 269 TCU e Indicadores de Conformidade' },
        { id: 'portal_spaguas', nome: '11. 🌊 Portal Institucional SP-Águas & Regimento', endpoint: 'https://www.spaguas.sp.gov.br', fallbackTipo: 'fonte_local', detalheLocal: 'Indexação Regimental da Deliberação nº 21/2026 e Decretos' }
    ];"""

for p in paths:
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    is_crlf = "\r\n" in c
    norm = c.replace("\r\n", "\n")

    # 1. Substituir as duas listas pelas matrizes canônicas de 11 motores
    norm = re.sub(r'MOTORES_PADRAO\s*=\s*\[[\s\S]*?\n\s*\];', nova_padrao, norm, count=1)
    norm = re.sub(r'(?:window\.)?MOTORES_CANONICOS_V9\s*=\s*\[[\s\S]*?\n\s*\];', nova_canonicos, norm, count=1)

    # 2. Invalidação de cache local storage
    cache_code = """        var m = JSON.parse(localStorage.getItem('motores_varredura') || 'null');
        var v = localStorage.getItem('sagti_motores_versao');
        if (!m || v !== 'v11.0_canonico_11_motores' || !Array.isArray(m) || m.length !== 11) {
            localStorage.removeItem('motores_varredura');
            localStorage.setItem('sagti_motores_versao', 'v11.0_canonico_11_motores');
            window.motoresVarredura = null;
        }"""
    norm = re.sub(r'var m = JSON\.parse\(localStorage\.getItem\(\'motores_varredura\'\)[\s\S]*?localStorage\.setItem\(\'sagti_motores_versao\', \'[^\']+\'\);\s*\}', cache_code.strip(), norm, count=1)

    # 3. Remover sobrescrita destrutiva em inicializarMotor1DoeSpV98
    norm = re.sub(r'if\s*\(Array\.isArray\(window\.MOTORES_CANONICOS_V9\)\s*&&\s*window\.MOTORES_CANONICOS_V9\[0\]\)\s*\{[\s\S]*?window\.MOTORES_CANONICOS_V9\[0\]\.detalheLocal\s*=[\s\S]*?\}', '// Preservar MariaDB no item 1 e DOE-SP no item 7', norm, count=1)

    # 4. Vincular o botão Buscar DOE-SP exclusivamente na linha 7 (DOE-SP)
    btn_wrapper = """var _origRenderTabelaMotores = window.renderizarTabelaMotores;
    window.renderizarTabelaMotores = function() {
        if (typeof _origRenderTabelaMotores === "function") {
            _origRenderTabelaMotores();
        }
        var tbody = document.getElementById("tbody-motores-varredura");
        if (!tbody) return;
        tbody.querySelectorAll("tr").forEach(function(row) {
            if (row.innerText.indexOf("Diário Oficial") !== -1 || row.innerText.indexOf("DOE-SP") !== -1) {
                var actionTd = row.lastElementChild;
                if (actionTd && actionTd.innerHTML.indexOf("abrirPainelMotor1DoeSp") === -1) {
                    actionTd.innerHTML =
                        '<button class="btn btn-primary" onclick="window.abrirPainelMotor1DoeSp(\\'SP-Águas\\')" style="padding:3px 8px;font-size:11px;margin-right:4px;background:#01a75f;border-color:#01a75f;">&#128269; Buscar DOE-SP</button>' +
                        actionTd.innerHTML;
                }
            }
        });
    };"""
    norm = re.sub(r'var _origRenderTabelaMotores = window\.renderizarTabelaMotores;[\s\S]*?actionTd\.innerHTML =[\s\S]*?actionTd\.innerHTML;\s*\}\s*\}\s*\};', btn_wrapper, norm, count=1)

    norm = norm.replace('⚙️ 2. Rotinas de Coleta &amp; Ações Operacionais</button>', '⚙️ 2. Rotinas de Coleta &amp; Ações Operacionais (11 Conectores)</button>')

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open(p, "w", encoding="utf-8") as f:
        f.write(final)
    print(f"✅ Sincronizado com sucesso: {p}")
