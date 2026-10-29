# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
os.makedirs(frontend_dir, exist_ok=True)

conector_js = r'''/**
 * Cockpit GTI — Conector Oficial de Telemetria e Navegação Reestruturada (4 Eixos)
 * SP-Águas SA-GTI
 */
(function () {
    // 1. ROTEADOR DE NAVEGAÇÃO E PERSISTÊNCIA DE ABA (HASH #tab)
    window.rotearAba = function (tabId) {
        if (!tabId) tabId = 'dashboards';

        // Atualiza URL hash se diferente
        if (window.location.hash !== '#' + tabId) {
            window.location.hash = '#' + tabId;
        }

        // Invoca o roteador nativo do painel
        if (typeof window.switchTab === 'function') {
            try {
                window.switchTab(tabId);
            } catch (e) {
                console.warn('Aviso switchTab:', e);
            }
        }

        // Atualiza o destaque ativo na sidebar
        document.querySelectorAll('.sidebar-menu .nav-item').forEach(function (el) {
            if (el.getAttribute('data-tab') === tabId) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });

        // Rola o scroll de visualização para o topo
        var cs = document.querySelector('.content-scroll') || document.querySelector('#main');
        if (cs && cs.scrollTop) {
            cs.scrollTop = 0;
        }
    };

    // 2. REESTRUTURAÇÃO DO MENU LATERAL (4 EIXOS LÓGICOS ENXUTOS NO PADRÃO NATIVO)
    function aplicarMenu4Eixos() {
        var sidebarMenu = document.querySelector('.sidebar-menu');
        if (!sidebarMenu) return;

        var htmlMenu = [
            '<div class="menu-category">VISÃO EXECUTIVA &amp; ESTRATÉGIA</div>',
            '<div class="nav-item active" data-tab="dashboards" onclick="window.rotearAba(\'dashboards\')">',
            '    <div class="nav-item-left">📊 <span>Central de Dashboards</span></div>',
            '    <span class="nav-badge">360°</span>',
            '</div>',
            '<div class="nav-item" data-tab="visao_estrategica" onclick="window.rotearAba(\'visao_estrategica\')">',
            '    <div class="nav-item-left">🎯 <span>Visão Estratégica &amp; Faróis</span></div>',
            '    <span class="nav-badge">87</span>',
            '</div>',
            '<div class="nav-item" data-tab="pdtic_eixos" onclick="window.rotearAba(\'pdtic_eixos\')">',
            '    <div class="nav-item-left">🧭 <span>PDTIC 2027-2030 &amp; KPIs</span></div>',
            '    <span class="nav-badge" style="background:#6366f1; color:#fff;">35</span>',
            '</div>',

            '<div class="menu-category">PORTFÓLIO &amp; PROJETOS OPENPROJECT</div>',
            '<div class="nav-item" data-tab="portfolio_openproject" onclick="window.rotearAba(\'portfolio_openproject\')">',
            '    <div class="nav-item-left">🏗️ <span>Portfólio OpenProject</span></div>',
            '    <span class="nav-badge" style="background:#10b981; color:#fff;">500</span>',
            '</div>',
            '<div class="nav-item" data-tab="tracks_sagti" onclick="window.rotearAba(\'tracks_sagti\')">',
            '    <div class="nav-item-left">⚡ <span>SA-GTI: Tracks &amp; Projetos</span></div>',
            '    <span class="nav-badge" style="background:#0544cf; color:#fff;">97</span>',
            '</div>',

            '<div class="menu-category">OPERAÇÃO, HELPDESK GLPI &amp; RITUAIS ÁGEIS</div>',
            '<div class="nav-item" data-tab="mesa_trabalho" onclick="window.rotearAba(\'mesa_trabalho\')">',
            '    <div class="nav-item-left">🖥️ <span>Mesa de Trabalho</span></div>',
            '    <span class="nav-badge" style="background:#00a859; color:white;">Demandas</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_glpi" onclick="window.rotearAba(\'gestao_glpi\')">',
            '    <div class="nav-item-left">🎫 <span>Gestão GLPI &amp; Helpdesk</span></div>',
            '    <span class="nav-badge" style="background:#0284c7; color:#fff;">203</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_agil" onclick="window.rotearAba(\'gestao_agil\')">',
            '    <div class="nav-item-left">📋 <span>Gestão Ágil &amp; Sprints</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="daily_warroom" onclick="window.rotearAba(\'daily_warroom\')">',
            '    <div class="nav-item-left">⏱️ <span>War Room: Daily &amp; Rituais</span></div>',
            '</div>',

            '<div class="menu-category">GOVERNANÇA SEI, IA &amp; CONFIGURAÇÕES</div>',
            '<div class="nav-item" data-tab="consulta" onclick="window.rotearAba(\'consulta\')">',
            '    <div class="nav-item-left">📁 <span>Acervo Probatório SEI</span></div>',
            '    <span class="nav-badge">179</span>',
            '</div>',
            '<div class="nav-item" data-tab="fixados" onclick="window.rotearAba(\'fixados\')">',
            '    <div class="nav-item-left">⭐ <span>Processos Fixados</span></div>',
            '    <span class="nav-badge" id="badge-fixados">0</span>',
            '</div>',
            '<div class="nav-item" data-tab="auditoria" onclick="window.rotearAba(\'auditoria\')">',
            '    <div class="nav-item-left">🛡️ <span>Auditoria TCE-SP &amp; IMR</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="esteira_ia" onclick="window.rotearAba(\'esteira_ia\')">',
            '    <div class="nav-item-left">🤖 <span>Chat IA &amp; RACI</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="cadernos" onclick="window.rotearAba(\'cadernos\')">',
            '    <div class="nav-item-left">📚 <span>Cadernos &amp; Regimento</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="configuracoes" onclick="window.rotearAba(\'configuracoes\')">',
            '    <div class="nav-item-left">🔧 <span>Configurações &amp; Motores</span></div>',
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
        var sMariaDB = await checarStatusServico('/api/v1/mariadb/status');
        var sOllama = await checarStatusServico('/api/v1/ia/status');
        var sGlpi = await checarStatusServico('/api/v1/glpi/status');
        var sOpenProject = await checarStatusServico('/api/v1/openproject/status');
        var sNewApi = await checarStatusServico('/api/v1/newapi/status');

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
            containerInfra.style.margin = '0 12px';
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
            if (elRef) {
                topbar.insertBefore(containerInfra, elRef);
            } else {
                topbar.appendChild(containerInfra);
            }

            var btnRec = document.getElementById('btn-recarregar-infra');
            if (btnRec) btnRec.addEventListener('click', atualizarTelemetria);
        }
    }

    // 5. INICIALIZAÇÃO
    function init() {
        aplicarMenu4Eixos();
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

print("Navegacao dos 4 Eixos e Roteador restaurados com sucesso!")
