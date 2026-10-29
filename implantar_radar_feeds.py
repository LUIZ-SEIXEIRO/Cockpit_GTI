# -*- coding: utf-8 -*-
import os, re

# 1. ATUALIZAR main.py COM AS ROTAS DA API DE FEEDS DO MARIADB
caminho_main = os.path.join(os.getcwd(), "main.py")
if os.path.exists(caminho_main):
    with open(caminho_main, "r", encoding="utf-8") as f:
        conteudo_main = f.read()

    if "/api/v1/feeds/publicacoes" not in conteudo_main:
        bloco_feeds = '''

# --- ROTAS DE FEEDS EXTERNOS (MARIADB: DOE-SP & PNCP UASG 262101) ---
@app.route('/api/v1/feeds/publicacoes')
def listar_feeds_publicacoes():
    import pymysql
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='glpi',
            password='glpi',
            database='glpidb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, fonte, identificador, 
                       DATE_FORMAT(data_publicacao, '%Y-%m-%d') as data_publicacao,
                       titulo, resumo, link_original, categoria,
                       DATE_FORMAT(data_coleta, '%Y-%m-%d %H:%i:%s') as data_coleta
                FROM feed_publicacoes_externas
                ORDER BY data_publicacao DESC, id DESC
                LIMIT 100
            """)
            linhas = cur.fetchall()
        conn.close()
        return jsonify({"status": "sucesso", "total": len(linhas), "itens": linhas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e), "itens": []}), 500

@app.route('/api/v1/feeds/sincronizar', methods=['POST', 'GET'])
def sincronizar_feeds_externos():
    import pymysql, requests
    inseridos = 0
    erros = []
    try:
        conn = pymysql.connect(
            host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4'
        )
        cur = conn.cursor()

        # 1. PNCP (UASG 262101 - SP-Águas)
        try:
            r_pncp = requests.get('http://localhost:5000/api/v1/pncp/editais', timeout=5)
            if r_pncp.ok:
                for item in r_pncp.json().get('itens', []):
                    ident = f"PNCP-2026-ITEM-{item.get('numeroItem', 0)}"
                    tit = item.get('objeto', '')
                    res = f"Status: {item.get('status')} | Valor Estimado: {item.get('valorEstimado')}"
                    cur.execute("""
                        INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria, link_original)
                        VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
                    """, ('PNCP', ident, tit, res, 'Licitacoes e Contratos', 'https://pncp.gov.br/app/editais?q=262101'))
                    inseridos += 1
        except Exception as ep:
            erros.append(f"PNCP: {str(ep)}")

        # 2. Diário Oficial (DOE-SP)
        try:
            r_doe = requests.get('http://localhost:5000/api/v1/doesp/publicacoes', timeout=5)
            if r_doe.ok:
                res_doe = r_doe.json()
                itens_doe = res_doe.get('itens', res_doe.get('publicacoes', []))
                for idx, item in enumerate(itens_doe, start=1):
                    ident = f"DOE-2026-PUB-{idx}"
                    tit = str(item.get('titulo', item.get('objeto', 'Publicacao Oficial SP-Aguas')))
                    res = f"Caderno: {item.get('caderno', 'Executivo')} | Secao: {item.get('secao', 'Atos')}"
                    cur.execute("""
                        INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria, link_original)
                        VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
                    """, ('DOE-SP', ident, tit, res, 'Diario Oficial', 'https://www.doe.sp.gov.br'))
                    inseridos += 1
        except Exception as ed:
            erros.append(f"DOE: {str(ed)}")

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "sucesso", "itens_processados": inseridos, "erros": erros})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
'''
        idx_main = conteudo_main.rfind("if __name__")
        if idx_main != -1:
            novo_main = conteudo_main[:idx_main] + bloco_feeds + "\n\n" + conteudo_main[idx_main:]
        else:
            novo_main = conteudo_main + bloco_feeds

        with open(caminho_main, "w", encoding="utf-8") as f:
            f.write(novo_main)
        print("1. Rotas de feeds registradas no main.py com sucesso!")
    else:
        print("1. Rotas de feeds já existem no main.py.")

# 2. ATUALIZAR conector_api.js COM A VIEW DO RADAR DE PUBLICAÇÕES
frontend_dir = os.path.join(os.getcwd(), "frontend")
os.makedirs(frontend_dir, exist_ok=True)

conector_js = r'''/**
 * Cockpit GTI — Conector Oficial de Telemetria, Navegação 5 Pilares e Radar de Feeds
 * SP-Águas SA-GTI
 */
(function () {
    window.DADOS_FEEDS_CACHE = [];
    window.FILTRO_FEED_FONTE_ATIVO = 'todos';

    // 1. ROTEADOR DE NAVEGAÇÃO E PERSISTÊNCIA DE ABA (HASH #tab)
    window.rotearAba = function (tabId) {
        if (!tabId) tabId = 'dashboards';

        if (window.location.hash !== '#' + tabId) {
            window.location.hash = '#' + tabId;
        }

        if (tabId === 'radar_publicacoes') {
            document.querySelectorAll('.tab-view').forEach(function (v) { v.style.display = 'none'; });
            var vRadar = document.getElementById('view-radar_publicacoes');
            if (vRadar) vRadar.style.display = 'block';
            window.carregarFeedsPublicacoes();
        } else {
            var vRadarOut = document.getElementById('view-radar_publicacoes');
            if (vRadarOut) vRadarOut.style.display = 'none';
            if (typeof window.switchTab === 'function') {
                try {
                    window.switchTab(tabId);
                } catch (e) {
                    console.warn('Aviso switchTab:', e);
                }
            }
        }

        document.querySelectorAll('.sidebar-menu .nav-item').forEach(function (el) {
            if (el.getAttribute('data-tab') === tabId) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });

        var cs = document.querySelector('.content-scroll') || document.querySelector('#main');
        if (cs && cs.scrollTop) {
            cs.scrollTop = 0;
        }
    };

    // 2. MENU LATERAL EM 5 PILARES COM O RADAR DE PUBLICAÇÕES
    function aplicarMenu5Pilares() {
        var sidebarMenu = document.querySelector('.sidebar-menu');
        if (!sidebarMenu) return;

        var htmlMenu = [
            '<div class="menu-category">1. VISÃO EXECUTIVA &amp; LIDERANÇA</div>',
            '<div class="nav-item active" data-tab="dashboards" onclick="window.rotearAba(\'dashboards\')">',
            '    <div class="nav-item-left">📊 <span>Central de Dashboards 360°</span></div>',
            '    <span class="nav-badge">360°</span>',
            '</div>',
            '<div class="nav-item" data-tab="visao_estrategica" onclick="window.rotearAba(\'visao_estrategica\')">',
            '    <div class="nav-item-left">🎯 <span>Faróis de Criticidade &amp; Prazos</span></div>',
            '    <span class="nav-badge">87</span>',
            '</div>',
            '<div class="nav-item" data-tab="portfolio_openproject" onclick="window.rotearAba(\'portfolio_openproject\')">',
            '    <div class="nav-item-left">🏗️ <span>Portfólio Geral OpenProject</span></div>',
            '    <span class="nav-badge" style="background:#10b981; color:#fff;">500</span>',
            '</div>',

            '<div class="menu-category">2. GESTÃO DE TIC &amp; CONTRATOS</div>',
            '<div class="nav-item" data-tab="tracks_sagti" onclick="window.rotearAba(\'tracks_sagti\')">',
            '    <div class="nav-item-left">⚡ <span>Tracks 1 &amp; 2 (Operação &amp; Contratos)</span></div>',
            '    <span class="nav-badge" style="background:#0544cf; color:#fff;">97</span>',
            '</div>',
            '<div class="nav-item" data-tab="pdtic_eixos" onclick="window.rotearAba(\'pdtic_eixos\')">',
            '    <div class="nav-item-left">🧭 <span>Governança PDTIC 2027-2030 &amp; KPIs</span></div>',
            '    <span class="nav-badge" style="background:#6366f1; color:#fff;">35</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_glpi" onclick="window.rotearAba(\'gestao_glpi\')">',
            '    <div class="nav-item-left">🎫 <span>Atendimento GLPI 10 (ITSM)</span></div>',
            '    <span class="nav-badge" style="background:#0284c7; color:#fff;">203</span>',
            '</div>',
            '<div class="nav-item" data-tab="consulta" onclick="window.rotearAba(\'consulta\')">',
            '    <div class="nav-item-left">📁 <span>Acervo Probatório SEI-SP</span></div>',
            '    <span class="nav-badge">179</span>',
            '</div>',

            '<div class="menu-category">3. OPERAÇÃO ÁGIL &amp; RITUAIS</div>',
            '<div class="nav-item" data-tab="mesa_trabalho" onclick="window.rotearAba(\'mesa_trabalho\')">',
            '    <div class="nav-item-left">🖥️ <span>Mesa de Trabalho Operacional</span></div>',
            '    <span class="nav-badge" style="background:#00a859; color:white;">Demandas</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_agil" onclick="window.rotearAba(\'gestao_agil\')">',
            '    <div class="nav-item-left">📋 <span>Sprint Planning &amp; Kanban</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="daily_warroom" onclick="window.rotearAba(\'daily_warroom\')">',
            '    <div class="nav-item-left">⏱️ <span>War Room Daily Scrum</span></div>',
            '</div>',

            '<div class="menu-category">4. INTELIGÊNCIA &amp; CONFORMIDADE</div>',
            '<div class="nav-item" data-tab="esteira_ia" onclick="window.rotearAba(\'esteira_ia\')">',
            '    <div class="nav-item-left">🤖 <span>Assistente Pessoal IA &amp; RACI</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="radar_publicacoes" onclick="window.rotearAba(\'radar_publicacoes\')">',
            '    <div class="nav-item-left">📡 <span>Radar DOE-SP &amp; PNCP</span></div>',
            '    <span class="nav-badge" style="background:#10b981; color:#fff;" id="badge-total-feeds">--</span>',
            '</div>',
            '<div class="nav-item" data-tab="auditoria" onclick="window.rotearAba(\'auditoria\')">',
            '    <div class="nav-item-left">🛡️ <span>Hub de Auditoria TCE-SP &amp; IMR</span></div>',
            '</div>',

            '<div class="menu-category">5. GOVERNANÇA, CADERNOS &amp; INFRA</div>',
            '<div class="nav-item" data-tab="cadernos" onclick="window.rotearAba(\'cadernos\')">',
            '    <div class="nav-item-left">📚 <span>Cadernos Temáticos &amp; Minutas A4</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="fixados" onclick="window.rotearAba(\'fixados\')">',
            '    <div class="nav-item-left">⭐ <span>Processos Fixados (Watchlist)</span></div>',
            '    <span class="nav-badge" id="badge-fixados">0</span>',
            '</div>',
            '<div class="nav-item" data-tab="configuracoes" onclick="window.rotearAba(\'configuracoes\')">',
            '    <div class="nav-item-left">🔧 <span>Telemetria, Motores &amp; RBAC</span></div>',
            '</div>'
        ].join('\n');

        sidebarMenu.innerHTML = htmlMenu;
    }

    // 3. INJEÇÃO DA VIEW DO RADAR DE PUBLICAÇÕES
    function injetarViewRadarPublicacoes() {
        var contentScroll = document.querySelector('.content-scroll') || document.querySelector('#main');
        if (!contentScroll || document.getElementById('view-radar_publicacoes')) return;

        var divView = document.createElement('div');
        divView.id = 'view-radar_publicacoes';
        divView.className = 'tab-view';
        divView.style.display = 'none';

        divView.innerHTML = [
            '<div class="page-banner" style="background: linear-gradient(135deg, #0f2d59 0%, #0070ba 50%, #00a859 100%); padding: 18px 24px; border-radius: 10px; color: #fff; margin-bottom: 20px;">',
            '    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">',
            '        <div>',
            '            <h3 style="margin: 0; font-size: 18px; font-weight: 800;">📡 RADAR DE PUBLICAÇÕES OFICIAIS &amp; EDITAIS (DOE-SP &amp; PNCP UASG 262101)</h3>',
            '            <p style="margin: 4px 0 0; font-size: 12px; color: #e2e8f0;">Monitoramento contínuo persistido no MariaDB (glpidb.feed_publicacoes_externas) &bull; Rastreabilidade jurídica e conformidade</p>',
            '        </div>',
            '        <button id="btn-sincronizar-feeds" onclick="window.dispararSincronizacaoFeeds()" class="btn btn-primary" style="background: #10b981; border-color: #10b981; font-weight: 700; font-size: 12px; padding: 8px 16px; cursor: pointer;">',
            '            🔄 Sincronizar Feeds Agora',
            '        </button>',
            '    </div>',
            '</div>',

            '<div class="kpi-row" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px;">',
            '    <div class="kpi-card" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">',
            '        <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Total Publicações</div>',
            '        <div id="kpi-feed-total" style="font-size: 24px; font-weight: 800; color: #002d5a; margin-top: 4px;">0</div>',
            '        <div style="font-size: 11px; color: #10b981; margin-top: 2px;">🟢 Base MariaDB Sincronizada</div>',
            '    </div>',
            '    <div class="kpi-card" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">',
            '        <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Diário Oficial (DOE-SP)</div>',
            '        <div id="kpi-feed-doe" style="font-size: 24px; font-weight: 800; color: #0284c7; margin-top: 4px;">0</div>',
            '        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Cadernos Executivo I &amp; II</div>',
            '    </div>',
            '    <div class="kpi-card" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">',
            '        <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Editais PNCP (UASG 262101)</div>',
            '        <div id="kpi-feed-pncp" style="font-size: 24px; font-weight: 800; color: #059669; margin-top: 4px;">0</div>',
            '        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Licitações SP-Águas</div>',
            '    </div>',
            '    <div class="kpi-card" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">',
            '        <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Última Atualização</div>',
            '        <div id="kpi-feed-hora" style="font-size: 18px; font-weight: 800; color: #475569; margin-top: 8px;">--:--:--</div>',
            '        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Auto-Refresh Ativo</div>',
            '    </div>',
            '</div>',

            '<div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">',
            '    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">',
            '        <div style="display: flex; gap: 8px; align-items: center;">',
            '            <button onclick="window.filtrarTabelaFeeds(\'todos\')" id="btn-filtro-feed-todos" class="btn btn-primary" style="font-size: 11px; padding: 5px 12px; background: #002d5a; border-color: #002d5a; cursor: pointer;">Todos</button>',
            '            <button onclick="window.filtrarTabelaFeeds(\'DOE-SP\')" id="btn-filtro-feed-doe" class="btn btn-secondary" style="font-size: 11px; padding: 5px 12px; cursor: pointer;">DOE-SP</button>',
            '            <button onclick="window.filtrarTabelaFeeds(\'PNCP\')" id="btn-filtro-feed-pncp" class="btn btn-secondary" style="font-size: 11px; padding: 5px 12px; cursor: pointer;">PNCP</button>',
            '        </div>',
            '        <input type="text" id="input-filtro-busca-feed" placeholder="🔍 Filtrar por título, processo ou objeto..." oninput="window.filtrarTabelaFeeds()" style="padding: 7px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; width: 320px;" />',
            '    </div>',

            '    <div style="overflow-x: auto;">',
            '        <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">',
            '            <thead>',
            '                <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1; color: #002d5a;">',
            '                    <th style="padding: 10px 12px; width: 90px;">Fonte</th>',
            '                    <th style="padding: 10px 12px; width: 150px;">Identificador</th>',
            '                    <th style="padding: 10px 12px; width: 100px;">Data</th>',
            '                    <th style="padding: 10px 12px;">Título / Objeto Oficial</th>',
            '                    <th style="padding: 10px 12px; width: 280px;">Resumo &amp; Status</th>',
            '                    <th style="padding: 10px 12px; text-align: center; width: 120px;">Ações</th>',
            '                </tr>',
            '            </thead>',
            '            <tbody id="tbody-radar-feeds">',
            '                <tr><td colspan="6" style="padding: 24px; text-align: center; color: #64748b;">Carregando publicações do MariaDB...</td></tr>',
            '            </tbody>',
            '        </table>',
            '    </div>',
            '</div>'
        ].join('\n');

        contentScroll.appendChild(divView);
    }

    // 4. CARREGAR E RENDERIZAR FEEDS DO MARIADB
    window.carregarFeedsPublicacoes = async function () {
        try {
            var resp = await fetch('/api/v1/feeds/publicacoes', { cache: 'no-store' });
            if (resp.ok) {
                var json = await resp.json();
                var itens = json.itens || [];
                window.DADOS_FEEDS_CACHE = itens;

                var total = itens.length;
                var totalDoe = itens.filter(function (it) { return it.fonte === 'DOE-SP'; }).length;
                var totalPncp = itens.filter(function (it) { return it.fonte === 'PNCP'; }).length;

                var elTot = document.getElementById('kpi-feed-total');
                var elDoe = document.getElementById('kpi-feed-doe');
                var elPncp = document.getElementById('kpi-feed-pncp');
                var elHora = document.getElementById('kpi-feed-hora');
                var elBadge = document.getElementById('badge-total-feeds');

                if (elTot) elTot.textContent = total;
                if (elDoe) elDoe.textContent = totalDoe;
                if (elPncp) elPncp.textContent = totalPncp;
                if (elHora) elHora.textContent = new Date().toLocaleTimeString('pt-BR');
                if (elBadge) elBadge.textContent = total;

                window.filtrarTabelaFeeds(window.FILTRO_FEED_FONTE_ATIVO);
            }
        } catch (e) {
            console.warn('Erro ao carregar feeds:', e);
        }
    };

    window.filtrarTabelaFeeds = function (fonte) {
        if (fonte) window.FILTRO_FEED_FONTE_ATIVO = fonte;
        var fAtiva = window.FILTRO_FEED_FONTE_ATIVO;

        ['todos', 'DOE-SP', 'PNCP'].forEach(function (f) {
            var btnId = f === 'todos' ? 'btn-filtro-feed-todos' : (f === 'DOE-SP' ? 'btn-filtro-feed-doe' : 'btn-filtro-feed-pncp');
            var btn = document.getElementById(btnId);
            if (btn) {
                if (f === fAtiva) {
                    btn.className = 'btn btn-primary';
                    btn.style.background = '#002d5a';
                    btn.style.borderColor = '#002d5a';
                    btn.style.color = '#fff';
                } else {
                    btn.className = 'btn btn-secondary';
                    btn.style.background = '#f1f5f9';
                    btn.style.borderColor = '#cbd5e1';
                    btn.style.color = '#334155';
                }
            }
        });

        var busca = (document.getElementById('input-filtro-busca-feed')?.value || '').toLowerCase().trim();
        var lista = window.DADOS_FEEDS_CACHE || [];

        var filtrados = lista.filter(function (it) {
            if (fAtiva !== 'todos' && it.fonte !== fAtiva) return false;
            if (busca) {
                var blob = (it.identificador + ' ' + it.titulo + ' ' + it.resumo + ' ' + it.categoria).toLowerCase();
                if (blob.indexOf(busca) === -1) return false;
            }
            return true;
        });

        var tbody = document.getElementById('tbody-radar-feeds');
        if (!tbody) return;

        if (filtrados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 24px; text-align: center; color: #64748b;">Nenhuma publicação localizada para os filtros selecionados.</td></tr>';
            return;
        }

        tbody.innerHTML = filtrados.map(function (it) {
            var badgeFonte = it.fonte === 'PNCP'
                ? '<span style="background: #dcfce7; color: #166534; font-weight: 700; font-size: 10.5px; padding: 3px 8px; border-radius: 12px;">PNCP</span>'
                : '<span style="background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 10.5px; padding: 3px 8px; border-radius: 12px;">DOE-SP</span>';

            var linkBtn = it.link_original
                ? '<a href="' + it.link_original + '" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="font-size: 10.5px; padding: 3px 8px; text-decoration: none; color: #002d5a; font-weight: 700;">🔗 Ver Link &#8599;</a>'
                : '<span style="color: #94a3b8; font-size: 11px;">--</span>';

            return '<tr style="border-bottom: 1px solid #e2e8f0;">' +
                '<td style="padding: 10px 12px;">' + badgeFonte + '</td>' +
                '<td style="padding: 10px 12px; font-family: monospace; font-size: 11px; color: #334155; font-weight: 600;">' + (it.identificador || '--') + '</td>' +
                '<td style="padding: 10px 12px; font-size: 11.5px; color: #64748b;">' + (it.data_publicacao || '--') + '</td>' +
                '<td style="padding: 10px 12px; font-weight: 700; color: #0f172a; font-size: 12px;">' + (it.titulo || '') + '</td>' +
                '<td style="padding: 10px 12px; font-size: 11px; color: #475569; line-height: 1.4;">' + (it.resumo || '') + '</td>' +
                '<td style="padding: 10px 12px; text-align: center;">' + linkBtn + '</td>' +
                '</tr>';
        }).join('');
    };

    window.dispararSincronizacaoFeeds = async function () {
        var btn = document.getElementById('btn-sincronizar-feeds');
        var textoOrig = btn ? btn.textContent : '';
        if (btn) {
            btn.textContent = '⏳ Sincronizando com MariaDB...';
            btn.disabled = true;
        }

        try {
            var r = await fetch('/api/v1/feeds/sincronizar', { method: 'POST' });
            if (r.ok) {
                var j = await r.json();
                await window.carregarFeedsPublicacoes();
                if (btn) btn.textContent = '✅ Sincronizado (' + (j.itens_processados || 0) + ' itens)';
            } else {
                if (btn) btn.textContent = '⚠️ Erro na captura';
            }
        } catch (e) {
            if (btn) btn.textContent = '⚠️ Falha de conexão';
        } finally {
            setTimeout(function () {
                if (btn) {
                    btn.textContent = textoOrig;
                    btn.disabled = false;
                }
            }, 2500);
        }
    };

    // 5. SINCRONISMO COM A URL HASH
    function sincAbaHash() {
        var hash = window.location.hash.replace('#', '').trim();
        if (hash) {
            window.rotearAba(hash);
        }
    }

    // 6. TELEMETRIA DA INFRAESTRUTURA (:5000)
    async function atualizarTelemetria() {
        var sMariaDB = false, sOllama = false, sGlpi = false, sOpenProject = false, sNewApi = false;
        try {
            var ctrl = new AbortController();
            var tid = setTimeout(function () { ctrl.abort(); }, 1800);
            var rStatus = await fetch('/api/v1/telemetria', { signal: ctrl.signal, cache: 'no-store' });
            clearTimeout(tid);
            if (rStatus.ok) {
                var json = await rStatus.json();
                sMariaDB = Boolean(json.mariadb);
                sOllama = Boolean(json.ollama);
                sGlpi = Boolean(json.glpi);
                sOpenProject = Boolean(json.openproject);
                sNewApi = Boolean(json.newapi);
            }
        } catch (eUni) {}

        var elMariaDB = document.getElementById('led-mariadb');
        var elOllama = document.getElementById('led-ollama');
        var elGlpi = document.getElementById('led-glpi');
        var elOp = document.getElementById('led-openproject');
        var elNewApi = document.getElementById('led-newapi');

        if (elMariaDB) elMariaDB.textContent = sMariaDB ? '🟢' : '🔴';
        if (elOllama) elOllama.textContent = sOllama ? '🟢' : '🔴';
        if (elGlpi) elGlpi.textContent = sGlpi ? '🟢' : '🔴';
        if (elOp) elOp.textContent = sOpenProject ? '🟢' : '🔴';
        if (elNewApi) elNewApi.textContent = sNewApi ? '🟢' : '🔴';

        var elSinc = document.getElementById('tempo-sinc');
        if (elSinc) {
            var agora = new Date();
            elSinc.textContent = agora.toLocaleTimeString('pt-BR');
        }
    }

    function montarWidgetInfra() {
        var topbar = document.querySelector('.topbar') || document.querySelector('#topbar') || document.querySelector('header');
        if (!topbar) return;

        var containerInfra = document.getElementById('widget-infra-cockpit');
        if (!containerInfra) {
            containerInfra = document.createElement('div');
            containerInfra.id = 'widget-infra-cockpit';
            containerInfra.style.display = 'inline-flex';
            containerInfra.style.alignItems = 'center';
            containerInfra.style.gap = '8px';
            containerInfra.style.margin = '0 10px';
            containerInfra.style.flexShrink = '0';

            containerInfra.innerHTML = [
                '<div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 16px; font-size: 11px; color: #334155;">',
                '    <span style="font-weight: 700; letter-spacing: 0.5px; color: #0f172a;">INFRA :5000</span>',
                '    <span id="led-mariadb" title="MariaDB (:3306)">🟢</span>',
                '    <span id="led-ollama" title="Ollama (:11434)">🟢</span>',
                '    <span id="led-glpi" title="GLPI Produção (Read-Only)">🟢</span>',
                '    <span id="led-openproject" title="OpenProject Produção (Trava SA-GTI)">🟢</span>',
                '    <span id="led-newapi" title="New API (:3001)">🟢</span>',
                '    <span style="color: #64748b; margin-left: 4px;">Sinc:</span>',
                '    <span id="tempo-sinc" style="font-weight: 600; color: #0f172a;">--:--:--</span>',
                '    <span id="btn-recarregar-infra" style="cursor: pointer; opacity: 0.8;" title="Recarregar Telemetria">🔄</span>',
                '</div>'
            ].join('\n');

            var elRef = topbar.querySelector('.user-pill') || topbar.querySelector('.user-profile') || topbar.querySelector('select') || null;
            if (elRef && elRef.parentNode) {
                elRef.parentNode.insertBefore(containerInfra, elRef);
            } else {
                topbar.appendChild(containerInfra);
            }

            var btnRec = document.getElementById('btn-recarregar-infra');
            if (btnRec) btnRec.addEventListener('click', atualizarTelemetria);
        }
    }

    // 7. INICIALIZAÇÃO
    function init() {
        aplicarMenu5Pilares();
        injetarViewRadarPublicacoes();
        montarWidgetInfra();
        atualizarTelemetria();
        window.carregarFeedsPublicacoes();
        sincAbaHash();
        window.addEventListener('hashchange', sincAbaHash);
        setInterval(atualizarTelemetria, 15000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
'''

caminho_js = os.path.join(frontend_dir, "conector_api.js")
with open(caminho_js, "w", encoding="utf-8") as f:
    f.write(conector_js)
print("2. conector_api.js atualizado com o Radar DOE-SP & PNCP e painel integrado!")
