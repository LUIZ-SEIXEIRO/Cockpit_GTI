# -*- coding: utf-8 -*-
import os, re

# 1. ATUALIZAR CONECTOR COM OS 5 PILARES EXECUTIVOS INTEGRADOS
frontend_dir = os.path.join(os.getcwd(), "frontend")
os.makedirs(frontend_dir, exist_ok=True)

conector_js = r'''/**
 * Cockpit GTI — Conector Oficial de Telemetria e Navegação em 5 Pilares Executivos
 * SP-Águas SA-GTI
 */
(function () {
    // 1. ROTEADOR DE NAVEGAÇÃO E PERSISTÊNCIA DE ABA (HASH #tab)
    window.rotearAba = function (tabId) {
        if (!tabId) tabId = 'dashboards';

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

    // 2. REESTRUTURAÇÃO DO MENU LATERAL EM 5 PILARES EXECUTIVOS INTEGRADOS
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

    // 3. SINCRONISMO COM A URL HASH
    function sincAbaHash() {
        var hash = window.location.hash.replace('#', '').trim();
        if (hash) {
            window.rotearAba(hash);
        }
    }

    // 4. TELEMETRIA DA INFRAESTRUTURA (:5000)
    async function checarStatusServico(url, timeoutMs) {
        timeoutMs = timeoutMs || 2500;
        try {
            var controller = new AbortController();
            var idTimeout = setTimeout(function () { controller.abort(); }, timeoutMs);
            var resp = await fetch(url, { signal: controller.signal, cache: 'no-store' });
            clearTimeout(idTimeout);
            return resp.ok;
        } catch (e) {
            return false;
        }
    }

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

        if (!sMariaDB && !sOllama && !sGlpi && !sOpenProject && !sNewApi) {
            sMariaDB = (await checarStatusServico('/api/v1/mariadb/status')) || (await checarStatusServico('/api/v1/db/status'));
            sOllama = (await checarStatusServico('/api/v1/ia/status'));
            sGlpi = (await checarStatusServico('/api/v1/glpi/status'));
            sOpenProject = (await checarStatusServico('/api/v1/openproject/status'));
            sNewApi = (await checarStatusServico('/api/v1/newapi/status'));
        }

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
print("1. conector_api.js atualizado com os 5 Pilares Executivos!")

# 2. ADICIONAR ROTA DE TELEMETRIA ROBUSTA NO main.py (SE AINDA NÃO EXISTIR)
caminho_main = os.path.join(os.getcwd(), "main.py")
if os.path.exists(caminho_main):
    with open(caminho_main, "r", encoding="utf-8") as f:
        conteudo_main = f.read()

    if "/api/v1/telemetria" not in conteudo_main:
        bloco_telemetria = '''

# --- ROTA DE TELEMETRIA DA INFRAESTRUTURA (:5000) ---
@app.route('/api/v1/telemetria')
def rota_telemetria_infra():
    import socket
    def test_p(h, p, t=0.8):
        try:
            s = socket.create_connection((h, p), timeout=t)
            s.close()
            return True
        except:
            return False

    return jsonify({
        "mariadb": test_p("127.0.0.1", 3306),
        "ollama": test_p("127.0.0.1", 11434),
        "glpi": test_p("10.199.43.26", 443) or test_p("127.0.0.1", 8088),
        "openproject": test_p("143.107.108.115", 443) or test_p("127.0.0.1", 8090),
        "newapi": test_p("127.0.0.1", 3001)
    })
'''
        idx_main = conteudo_main.rfind("if __name__")
        if idx_main != -1:
            novo_main = conteudo_main[:idx_main] + bloco_telemetria + "\n\n" + conteudo_main[idx_main:]
        else:
            novo_main = conteudo_main + bloco_telemetria

        with open(caminho_main, "w", encoding="utf-8") as f:
            f.write(novo_main)
        print("2. Rota /api/v1/telemetria registrada com sucesso no main.py!")
    else:
        print("2. Rota /api/v1/telemetria já existente no main.py.")
