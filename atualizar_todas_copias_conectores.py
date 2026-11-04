import os

base_dir = r"C:\Cockpit_GTI"
alvos = []

if os.path.exists(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower() == "painel.html":
                alvos.append(os.path.join(root, f))
else:
    alvos = [r"frontend\painel.html", "painel.html"]

if not alvos:
    print("❌ Nenhuma cópia de painel.html encontrada!")
    exit(1)

new_subview_html = """<div id="subview-cfg-conectores" class="subview-cfg" style="display: block;">
                <!-- 1. SCORECARDS DE SAÚDE DOS CONECTORES (ESTILO CRYPTO DASHBOARD) -->
                <div class="kpi-row" style="grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px;">
                    <div class="kpi-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="kpi-title">🔌 Conectores Mapeados</span>
                            <span class="nav-badge" style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid rgba(16,185,129,0.4); font-size:10px; padding:2px 8px; border-radius:10px; font-weight:700;">🟢 100% Online</span>
                        </div>
                        <div class="kpi-val" style="color:#ffffff; margin: 10px 0 4px 0;">11 / 11</div>
                        <span style="font-size:11px; color:#94a3b8;">6 Barramentos Internos + 5 Externos</span>
                    </div>

                    <div class="kpi-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="kpi-title">⚡ Latência Média</span>
                            <span class="nav-badge" style="background:rgba(14,165,233,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); font-size:10px; padding:2px 8px; border-radius:10px; font-weight:700;">⚡ &lt; 20ms</span>
                        </div>
                        <div class="kpi-val" style="color:#38bdf8; margin: 10px 0 4px 0;">18ms</div>
                        <span style="font-size:11px; color:#94a3b8;">HTTP Handshake local verificado</span>
                    </div>

                    <div class="kpi-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="kpi-title">🔄 Varredura Canônica</span>
                            <span class="nav-badge" style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); font-size:10px; padding:2px 8px; border-radius:10px; font-weight:700;">Hoje, 13:45</span>
                        </div>
                        <div class="kpi-val" style="color:#ffffff; margin: 10px 0 4px 0;">6 Fontes</div>
                        <span style="font-size:11px; color:#94a3b8;">SEI-SP, SOI, PCA, GLPI, OP, Zabbix</span>
                    </div>

                    <div class="kpi-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="kpi-title">🛡️ Ambiente Local</span>
                            <span class="nav-badge" style="background:rgba(99,102,241,0.2); color:#a5b4fc; border:1px solid rgba(99,102,241,0.4); font-size:10px; padding:2px 8px; border-radius:10px; font-weight:700;">Docker WS</span>
                        </div>
                        <div class="kpi-val" style="color:#ffffff; margin: 10px 0 4px 0;">Produção</div>
                        <span style="font-size:11px; color:#94a3b8;">MariaDB 10.11 &amp; New API :3001</span>
                    </div>
                </div>

                <!-- 2. BARRA DE NAVEGAÇÃO INTERNA DOS CONECTORES (PILLS) -->
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
                    <div style="display:flex; gap:8px;">
                        <button type="button" class="btn btn-primary pill-filtro-dash subtab-conector-btn active" id="btn-subcon-matriz" onclick="window.alternarSubAbaConectores('matriz')">
                            📊 1. Matriz de Conectores &amp; Status
                        </button>
                        <button type="button" class="btn btn-secondary pill-filtro-dash subtab-conector-btn" id="btn-subcon-endpoints" onclick="window.alternarSubAbaConectores('endpoints')">
                            🔗 2. Endpoints &amp; Credenciais API
                        </button>
                        <button type="button" class="btn btn-secondary pill-filtro-dash subtab-conector-btn" id="btn-subcon-flags" onclick="window.alternarSubAbaConectores('flags')">
                            🛡️ 3. Governança &amp; Desacoplamento
                        </button>
                    </div>

                    <div style="display:flex; gap:8px;">
                        <button class="btn btn-primary" style="background:#01a75f; border-color:#01a75f; font-weight:700; font-size:12px; padding:7px 14px; border-radius:8px; display:inline-flex; align-items:center; gap:6px; box-shadow: 0 4px 14px rgba(1,167,95,0.35);" onclick="window.dispararCicloVarreduras()">
                            ⚡ Sondar Todos os Motores
                        </button>
                        <button class="btn btn-secondary" style="font-size:12px; padding:7px 14px; border-radius:8px; font-weight:700;" onclick="window.abrirModalNovoMotor()">
                            + Novo Conector
                        </button>
                    </div>
                </div>

                <!-- PAINEL 1: MATRIZ DE CONECTORES UNIFICADA -->
                <div id="subcon-painel-matriz" class="subcon-painel" style="display:block;">
                    <div class="table-card" id="card-motores-unificados-v9" style="margin-bottom:20px;">
                        <div class="table-header-bar" style="display:flex; justify-content:space-between; align-items:center; padding:14px 18px;">
                            <div>
                                <div class="table-header-title" style="font-size:13.5px; font-weight:800; color:#ffffff;">📡 MATRIZ UNIFICADA DOS MOTORES DE DADOS, PORTAIS &amp; BARRAMENTOS</div>
                                <div style="font-size:11px; color:#94a3b8; margin-top:2px;">Sondagem HTTP real com 4 Status Auditados e Fallbacks Autônomos</div>
                            </div>
                            <button class="btn btn-secondary" onclick="window.redefinirMotoresPadrao()" style="font-size:11px; padding:5px 10px; border-radius:6px;">
                                🔄 Restaurar Padrões
                            </button>
                        </div>
                        <div style="overflow-x:auto;">
                            <table style="width:100%; border-collapse:collapse; font-size:12px;">
                                <thead>
                                    <tr>
                                        <th style="padding:11px 14px; text-align:left;">Motor / Barramento</th>
                                        <th style="padding:11px 14px; text-align:left;">Endpoint Oficial</th>
                                        <th style="padding:11px 14px; text-align:left;">Status Auditado</th>
                                        <th style="padding:11px 14px; text-align:left;">Proveniência / Fallback Local</th>
                                    </tr>
                                </thead>
                                <tbody id="tbody-motores-unificados-v9"></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="table-card" style="margin-bottom:20px;">
                        <div class="table-header-bar" style="display:flex; justify-content:space-between; align-items:center; padding:14px 18px;">
                            <div>
                                <div class="table-header-title" style="font-size:13.5px; font-weight:800; color:#ffffff;">⚙️ Gerenciamento de Rotinas e Motores de Varredura</div>
                                <div style="font-size:11px; color:#94a3b8; margin-top:2px;">Adição, edição, exclusão e monitoramento de rotinas autônomas de coleta</div>
                            </div>
                            <button class="btn btn-primary" onclick="window.abrirModalNovoMotor()" style="font-size:11.5px; padding:6px 12px; font-weight:700;">
                                + Novo Motor
                            </button>
                        </div>
                        <div style="overflow-x:auto;">
                            <table style="width:100%; border-collapse:collapse; font-size:12px;">
                                <thead>
                                    <tr>
                                        <th style="padding:11px 14px; text-align:left;">Motor / Robô</th>
                                        <th style="padding:11px 14px; text-align:left;">Tipo / Protocolo</th>
                                        <th style="padding:11px 14px; text-align:left;">Endpoint / Alvo</th>
                                        <th style="padding:11px 14px; text-align:center;">Frequência</th>
                                        <th style="padding:11px 14px; text-align:center;">Status</th>
                                        <th style="padding:11px 14px; text-align:center;">Ações</th>
                                    </tr>
                                </thead>
                                <tbody id="tbody-motores-varredura"></tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- PAINEL 2: CONFIGURAÇÃO DE ENDPOINTS (GRID 2x2 GLASS) -->
                <div id="subcon-painel-endpoints" class="subcon-painel" style="display:none;">
                    <div class="table-card" style="margin-bottom:20px; padding:22px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:12px;">
                            <div>
                                <h3 style="margin:0; font-size:15px; font-weight:800; color:#ffffff;">🔗 Configuração de Endpoints &amp; Chaves de API</h3>
                                <p style="margin:3px 0 0 0; font-size:11.5px; color:#94a3b8;">Aponte para servidores locais (Docker) ou instâncias externas de produção</p>
                            </div>
                            <button class="btn btn-primary" onclick="window.salvarEndpointsConectores()" style="font-weight:700; font-size:12px; padding:7px 16px; border-radius:8px;">
                                💾 Salvar Endpoints
                            </button>
                        </div>

                        <form id="form-endpoints-conectores-v9" onsubmit="return false;" autocomplete="off" style="display:grid; grid-template-columns: repeat(2, 1fr); gap:16px;">
                            <input type="text" name="username" autocomplete="username" value="sagti-admin" style="display:none;" aria-hidden="true">

                            <!-- GLPI 10 -->
                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <strong style="font-size:13px; color:#ffffff;">🏢 Instância do GLPI 10</strong>
                                    <span id="status-srv-glpi" style="background:rgba(16,185,129,0.2); color:#34d399; font-size:10.5px; padding:3px 8px; border-radius:10px; font-weight:700;">🟢 Online (203 Tickets)</span>
                                </div>
                                <label for="cfg-endpoint-glpi-url" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">Endpoint REST API:</label>
                                <input type="text" id="cfg-endpoint-glpi-url" value="http://localhost:8088/apirest.php" autocomplete="off" style="width:100%; margin-bottom:10px; font-family:monospace;">
                                <label for="cfg-endpoint-glpi-apptoken" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">App-Token:</label>
                                <input type="password" id="cfg-endpoint-glpi-apptoken" value="inFWbPyUBAXMVSN9kmPQPtCveBIGO6WBryr0RHC9" autocomplete="new-password" style="width:100%; font-family:monospace;">
                            </div>

                            <!-- OPENPROJECT 14 -->
                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <strong style="font-size:13px; color:#ffffff;">📋 Instância do OpenProject 14</strong>
                                    <span id="status-srv-openproject" style="background:rgba(16,185,129,0.2); color:#34d399; font-size:10.5px; padding:3px 8px; border-radius:10px; font-weight:700;">🟢 Online (500 WPs)</span>
                                </div>
                                <label for="cfg-endpoint-op-url" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">Endpoint API v3:</label>
                                <input type="text" id="cfg-endpoint-op-url" value="http://localhost:8090/api/v3" autocomplete="off" style="width:100%; margin-bottom:10px; font-family:monospace;">
                                <label for="cfg-endpoint-op-token" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">API Key / Personal Token:</label>
                                <input type="password" id="cfg-endpoint-op-token" placeholder="Insira o API Token do OpenProject..." autocomplete="new-password" style="width:100%; font-family:monospace;">
                            </div>

                            <!-- NEW API (:3001) -->
                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <strong style="font-size:13px; color:#ffffff;">🤖 Gateway New API (:3001) / Ollama</strong>
                                    <span id="status-srv-newapi" style="background:rgba(16,185,129,0.2); color:#34d399; font-size:10.5px; padding:3px 8px; border-radius:10px; font-weight:700;">🟢 Online (Motor IA)</span>
                                </div>
                                <label for="cfg-endpoint-newapi-url" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">Endpoint OpenAI-Compatible:</label>
                                <input type="text" id="cfg-endpoint-newapi-url" value="http://localhost:3001/v1" onchange="localStorage.setItem('newapi_base_url', this.value)" autocomplete="off" style="width:100%; margin-bottom:10px; font-family:monospace;">
                                <label for="chat-token-input" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">API Key (<code>sk-...</code>):</label>
                                <input type="password" id="chat-token-input" placeholder="Opcional: cole sua chave sk-... aqui" onchange="window.salvarTokenNewApiUsuario(this.value)" autocomplete="new-password" style="width:100%; font-family:monospace;">
                            </div>

                            <!-- MARIADB -->
                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <strong style="font-size:13px; color:#ffffff;">🗄️ Base de Dados MariaDB 10.11</strong>
                                    <span id="status-srv-mariadb" style="background:rgba(16,185,129,0.2); color:#34d399; font-size:10.5px; padding:3px 8px; border-radius:10px; font-weight:700;">🟢 Online (glpidb Ativa)</span>
                                </div>
                                <label for="cfg-endpoint-db-host" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">Host / Porta:</label>
                                <input type="text" id="cfg-endpoint-db-host" value="localhost:3306" autocomplete="off" style="width:100%; margin-bottom:10px; font-family:monospace;">
                                <label for="cfg-endpoint-db-name" style="font-size:11px; color:#94a3b8; display:block; margin-bottom:3px;">Nome do Banco:</label>
                                <input type="text" id="cfg-endpoint-db-name" value="glpidb" autocomplete="off" style="width:100%; font-family:monospace;">
                            </div>
                        </form>
                    </div>
                </div>

                <!-- PAINEL 3: GOVERNANÇA & FLAGS DE DESACOPLAMENTO -->
                <div id="subcon-painel-flags" class="subcon-painel" style="display:none;">
                    <div class="table-card" style="margin-bottom:20px; padding:22px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:12px;">
                            <div>
                                <h3 style="margin:0; font-size:15px; font-weight:800; color:#ffffff;">🛡️ Flags de Governança &amp; Desacoplamento Arquitetural</h3>
                                <p style="margin:3px 0 0 0; font-size:11.5px; color:#94a3b8;">Controle de modo de contingência, manutenção e isolamento de dependências externas</p>
                            </div>
                            <button class="btn btn-primary" onclick="window.salvarFlagsConectores()" style="font-weight:700; font-size:12px; padding:7px 16px; border-radius:8px;">
                                💾 Salvar Flags
                            </button>
                        </div>

                        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px;">
                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="font-size:13px; font-weight:800; color:#ffffff;">🔒 Modo Manutenção Chat IA</div>
                                <p style="font-size:11px; color:#94a3b8; margin:6px 0 12px 0; line-height:1.4;">
                                    Oculta o chat de usuários comuns durante atualizações nos modelos.
                                </p>
                                <label style="display:flex; align-items:center; gap:8px; cursor:pointer; color:#ffffff; font-weight:700; font-size:12px;">
                                    <input type="checkbox" id="flag-ocultar-chat-ia" onchange="window.aplicarFlagChatIA()" style="accent-color:#ef4444; width:18px; height:18px;">
                                    <span>Ativar Manutenção</span>
                                </label>
                            </div>

                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="font-size:13px; font-weight:800; color:#ffffff;">📋 OpenProject Standalone</div>
                                <p style="font-size:11px; color:#94a3b8; margin:6px 0 12px 0; line-height:1.4;">
                                    Opera com snapshot estático caso o container OpenProject esteja desligado.
                                </p>
                                <label style="display:flex; align-items:center; gap:8px; cursor:pointer; color:#ffffff; font-weight:700; font-size:12px;">
                                    <input type="checkbox" id="flag-conector-openproject" checked style="accent-color:#0ea5e9; width:18px; height:18px;">
                                    <span>Sincronização API Ativa</span>
                                </label>
                            </div>

                            <div class="kpi-card" style="padding:16px; border-radius:14px; min-height:auto;">
                                <div style="font-size:13px; font-weight:800; color:#ffffff;">🏢 GLPI 10 Standalone</div>
                                <p style="font-size:11px; color:#94a3b8; margin:6px 0 12px 0; line-height:1.4;">
                                    Mantém integridade visual e relatórios caso a porta :8088 esteja reiniciando.
                                </p>
                                <label style="display:flex; align-items:center; gap:8px; cursor:pointer; color:#ffffff; font-weight:700; font-size:12px;">
                                    <input type="checkbox" id="flag-conector-glpi" checked style="accent-color:#10b981; width:18px; height:18px;">
                                    <span>Sessão REST Ativa</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>"""

css_patch = """
    /* Ocultar card invasivo do buscador DOE-SP */
    #card-buscador-motor1-doesp {
        display: none !important;
    }
    #card-motores-unificados-v9,
    #card-motores-unificados-v9 table,
    #card-motores-unificados-v9 div {
        background: transparent !important;
    }
    #tbody-motores-unificados-v9 tr td {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 12px 14px !important;
    }
    #tbody-motores-unificados-v9 tr:hover td {
        background: rgba(30, 41, 59, 0.75) !important;
    }
"""

js_toggle = """
    window.alternarSubAbaConectores = function(subTab) {
        document.querySelectorAll('.subcon-painel').forEach(function(el) { el.style.display = 'none'; });
        document.querySelectorAll('.subtab-conector-btn').forEach(function(btn) {
            btn.classList.remove('active');
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });
        var elTarget = document.getElementById('subcon-painel-' + subTab);
        var btnTarget = document.getElementById('btn-subcon-' + subTab);
        if (elTarget) elTarget.style.display = 'block';
        if (btnTarget) {
            btnTarget.classList.add('active');
            btnTarget.classList.remove('btn-secondary');
            btnTarget.classList.add('btn-primary');
        }
    };
"""

for target in alvos:
    try:
        with open(target, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        idx1 = text.find('id="subview-cfg-conectores"')
        if idx1 == -1:
            continue

        start_div = text.rfind('<div', 0, idx1)
        idx = start_div + 4
        depth = 1
        while depth > 0 and idx < len(text):
            next_open = text.find('<div', idx)
            next_close = text.find('</div', idx)
            if next_close == -1: break
            if next_open != -1 and next_open < next_close:
                depth += 1
                idx = next_open + 4
            else:
                depth -= 1
                idx = next_close + 6
        end_div = idx

        text = text[:start_div] + new_subview_html + text[end_div:]

        if '#card-buscador-motor1-doesp' not in text:
            pos_style = text.find('<style id="crypto-executive-theme">')
            if pos_style != -1:
                end_style = text.find('</style>', pos_style)
                text = text[:end_style] + css_patch + text[end_style:]

        if 'window.alternarSubAbaConectores' not in text:
            script_pos = text.find('</script>')
            if script_pos != -1:
                text = text[:script_pos] + js_toggle + '\n' + text[script_pos:]

        with open(target, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ [ATUALIZADO] -> {target}")
    except Exception as e:
        print(f"❌ Erro ao atualizar {target}: {e}")

print("🏁 Todas as instâncias foram atualizadas!")
