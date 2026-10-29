# -*- coding: utf-8 -*-
import os, shutil

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_backup = os.path.join(frontend_dir, "painel_backup_pre_saneamento.html")

if not os.path.exists(caminho_painel):
    print("ERRO: painel.html não encontrado em", caminho_painel)
    exit(1)

# 1. BACKUP DE SEGURANÇA COM TIMESTAMP
shutil.copy2(caminho_painel, caminho_backup)
print(f"1. Backup de segurança criado em: {caminho_backup}")

with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

tam_inicial = len(text)
linhas_iniciais = len(text.splitlines())

# 2. INCORPORAR WATCHLIST DE FIXADOS DENTRO DA MESA DE TRABALHO
card_fixados_mesa = '''
            <!-- SEÇÃO DE PROCESSOS FIXADOS (WATCHLIST DO GESTOR) INCORPORADA -->
            <div class="table-card" style="margin-top: 18px; margin-bottom: 20px; border-top: 3px solid #b45309;">
                <div class="table-header-bar" style="background: #fffbeb; display: flex; justify-content: space-between; align-items: center; padding: 10px 16px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px;">⭐</span>
                        <div class="table-header-title" style="color: #92400e; font-size: 13px; font-weight: 700;">Watchlist Prioritária: Processos Fixados</div>
                    </div>
                    <span id="fixados-count-badge" style="background: #fef3c7; color: #92400e; font-weight: 700; font-size: 11px; padding: 2px 10px; border-radius: 12px; border: 1px solid #fde68a;">0 Processos</span>
                </div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 40px; text-align: center;">⭐</th>
                                <th>ID Processo</th>
                                <th>Especificação / Objeto</th>
                                <th>Responsável</th>
                                <th>Status</th>
                                <th>Aging</th>
                                <th style="text-align: center;">Ações</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-fixados">
                            <!-- Preenchido dinamicamente via renderizarFixados() -->
                        </tbody>
                    </table>
                </div>
            </div>
'''

pos_dash = text.find('id="view-dashboards"')
div_dash_start = text.rfind('<div', 0, pos_dash)
text = text[:div_dash_start] + card_fixados_mesa + "\n        </div>\n\n            " + text[div_dash_start:]

# 3. ELIMINAR A VIEW-FIXADOS ISOLADA
pos_fix = text.find('id="view-fixados"')
pos_vis = text.find('id="view-visao_estrategica"')
if pos_fix != -1 and pos_vis != -1:
    div_fix_start = text.rfind('<div', 0, pos_fix)
    div_vis_start = text.rfind('<div', 0, pos_vis)
    text = text[:div_fix_start] + text[div_vis_start:]

# 4. ELIMINAR SUBVIEW-CFG-AGENTES (39 KB REDUNDANTE EM CONFIGURAÇÕES)
pos_age = text.find('id="subview-cfg-agentes"')
pos_bck = text.find('id="subview-cfg-backup"')
if pos_age != -1 and pos_bck != -1:
    div_age_start = text.rfind('<div', 0, pos_age)
    div_bck_start = text.rfind('<div', 0, pos_bck)
    text = text[:div_age_start] + text[div_bck_start:]

# 5. ELIMINAR MASCOTE E GAVETA MORTA NO RODAPÉ DO DOM
pos_mascote = text.find('<!-- MASCOTE INTERATIVO DA SP-ÁGUAS')
pos_end_drawer = text.find('<!-- MODAIS GERAIS', pos_mascote)
if pos_end_drawer == -1: pos_end_drawer = text.find('<!-- MODAL', pos_mascote)
if pos_mascote != -1 and pos_end_drawer != -1:
    text = text[:pos_mascote] + text[pos_end_drawer:]

with open(caminho_painel, "w", encoding="utf-8") as f:
    f.write(text)

tam_final = len(text)
linhas_finais = len(text.splitlines())
economia_kb = (tam_inicial - tam_final) // 1024
economia_linhas = linhas_iniciais - linhas_finais
print(f"2. painel.html saneado com sucesso! Redução de ~{economia_kb} KB e {economia_linhas} linhas de código morto.")

# 6. ATUALIZAR conector_api.js COM A NAVEGAÇÃO DOS 5 PILARES CONSOLIDADA
conector_js = r'''/**
 * Cockpit GTI — Conector Oficial de Telemetria e Navegação em 5 Pilares Consolidados
 * SP-Águas SA-GTI
 */
(function () {
    // 1. ROTEADOR DE NAVEGAÇÃO E PERSISTÊNCIA DE ABA (HASH #tab)
    window.rotearAba = function (tabId) {
        if (!tabId) tabId = 'dashboards';

        // Redirecionamento transparente de fixados para a Mesa de Trabalho
        if (tabId === 'fixados') {
            tabId = 'mesa_trabalho';
            setTimeout(function() {
                var elF = document.getElementById('tbody-fixados');
                if (elF && elF.scrollIntoView) elF.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }

        if (window.location.hash !== '#' + tabId) {
            window.location.hash = '#' + tabId;
        }

        if (typeof window.switchTab === 'function') {
            try {
                window.switchTab(tabId);
            } catch (e) {
                console.warn('Aviso switchTab:', e);
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

    // 2. MENU LATERAL EM 5 PILARES (14 TELAS COESAS)
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
            '<div class="nav-item" data-tab="auditoria" onclick="window.rotearAba(\'auditoria\')">',
            '    <div class="nav-item-left">🛡️ <span>Hub de Auditoria TCE-SP &amp; IMR</span></div>',
            '</div>',

            '<div class="menu-category">5. GOVERNANÇA, CADERNOS &amp; INFRA</div>',
            '<div class="nav-item" data-tab="cadernos" onclick="window.rotearAba(\'cadernos\')">',
            '    <div class="nav-item-left">📚 <span>Cadernos Temáticos &amp; Minutas A4</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="configuracoes" onclick="window.rotearAba(\'configuracoes\')">',
            '    <div class="nav-item-left">🔧 <span>Central de Configurações &amp; RBAC</span></div>',
            '</div>'
        ].join('\n');

        sidebarMenu.innerHTML = htmlMenu;
    }

    // 3. SINCRONISMO COM A URL HASH
    function sincAbaHash() {
        var hash = window.location.hash.replace('#', '').trim();
        if (hash) {
            window.rotearAba(hash);
        }
    }

    // 4. TELEMETRIA DA INFRAESTRUTURA (:5000)
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

    // 5. INICIALIZAÇÃO
    function init() {
        aplicarMenu5Pilares();
        montarWidgetInfra();
        atualizarTelemetria();
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

print("3. conector_api.js atualizado com os 5 Pilares Consolidados!")
print("Saneamento da Etapa 1 concluído com sucesso!")
