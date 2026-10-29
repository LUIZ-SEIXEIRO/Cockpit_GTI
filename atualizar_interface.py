# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
os.makedirs(frontend_dir, exist_ok=True)

conector_js = r'''/**
 * Cockpit GTI — Conector Oficial de Telemetria e Motor Glassmorphism
 * SP-Águas SA-GTI
 */

(function () {
    // 1. INJEÇÃO DA FOLHA DE ESTILOS GLASSMORPHISM DINÂMICA
    const cssGlassmorphism = `
    /* =========================================================
       SP-ÁGUAS SA-GTI — GLASSMORPHISM SAAS (DARK & LIGHT)
       ========================================================= */

    :root {
        --sp-blue: #0070BA;
        --sp-green: #00A859;
        --sp-cyan: #00AEEF;
        --sp-transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* MODO ESCURO (DEFAULT) */
    html[data-theme="dark"], body[data-theme="dark"], body:not([data-theme="light"]) {
        --bg-main: #0B0F19;
        --bg-glass-card: rgba(17, 24, 39, 0.65);
        --bg-glass-card-hover: rgba(30, 41, 59, 0.78);
        --bg-glass-bar: rgba(11, 15, 25, 0.82);
        --bg-glass-sidebar: rgba(11, 15, 25, 0.90);
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glass-hover: rgba(255, 255, 255, 0.18);
        --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
        --text-primary: #FFFFFF;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --input-bg: rgba(255, 255, 255, 0.06);
        --input-border: rgba(255, 255, 255, 0.14);
        --table-row-hover: rgba(255, 255, 255, 0.04);
        --aurora-1: rgba(99, 102, 241, 0.15);
        --aurora-2: rgba(6, 182, 212, 0.12);
        --aurora-3: rgba(16, 185, 129, 0.08);
    }

    /* MODO CLARO */
    html[data-theme="light"], body[data-theme="light"] {
        --bg-main: #F8FAFC;
        --bg-glass-card: rgba(255, 255, 255, 0.78);
        --bg-glass-card-hover: rgba(255, 255, 255, 0.92);
        --bg-glass-bar: rgba(255, 255, 255, 0.88);
        --bg-glass-sidebar: rgba(255, 255, 255, 0.94);
        --border-glass: rgba(226, 232, 240, 0.85);
        --border-glass-hover: rgba(203, 213, 225, 1);
        --shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;
        --input-bg: rgba(255, 255, 255, 0.90);
        --input-border: #CBD5E1;
        --table-row-hover: rgba(241, 245, 249, 0.65);
        --aurora-1: rgba(99, 102, 241, 0.06);
        --aurora-2: rgba(6, 182, 212, 0.06);
        --aurora-3: rgba(16, 185, 129, 0.04);
    }

    /* FUNDO PRINCIPAL & AURORA GLOW */
    body {
        background-color: var(--bg-main) !important;
        background-image: 
            radial-gradient(at 0% 0%, var(--aurora-1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, var(--aurora-2) 0px, transparent 50%),
            radial-gradient(at 50% 50%, var(--aurora-3) 0px, transparent 60%) !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        transition: var(--sp-transition) !important;
    }

    /* TOPBAR TRANSLÚCIDA */
    .topbar, header, .navbar, .main-header {
        background: var(--bg-glass-bar) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-bottom: 1px solid var(--border-glass) !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-glass) !important;
        transition: var(--sp-transition) !important;
    }

    .topbar h1, .topbar h2, .topbar h3, .topbar h4, .topbar span, .topbar div {
        color: var(--text-primary) !important;
    }

    .topbar small, .topbar .text-muted, .topbar .subtitle {
        color: var(--text-secondary) !important;
    }

    /* SIDEBAR TRANSLÚCIDA */
    .sidebar, aside, .main-sidebar {
        background: var(--bg-glass-sidebar) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--border-glass) !important;
        color: var(--text-secondary) !important;
        box-shadow: var(--shadow-glass) !important;
        transition: var(--sp-transition) !important;
    }

    .sidebar .menu-title, .sidebar-heading, .sidebar small {
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }

    .sidebar a, .sidebar-link, .nav-link, .menu-item {
        color: var(--text-secondary) !important;
        transition: var(--sp-transition) !important;
        border-radius: 8px;
    }

    .sidebar a:hover, .sidebar-link:hover, .nav-link:hover, .menu-item:hover {
        background: var(--input-bg) !important;
        color: var(--text-primary) !important;
    }

    .sidebar .active, .sidebar-link.active, .nav-link.active, .menu-item.active {
        background: linear-gradient(90deg, rgba(0, 112, 186, 0.25), rgba(99, 102, 241, 0.15)) !important;
        border-left: 3px solid var(--sp-cyan) !important;
        color: var(--text-primary) !important;
        font-weight: 600;
    }

    /* CARDS EM FORMATO DE VIDRO FOSCO */
    .card, .stat-card, .box, .panel, .kpi-card, .bg-white, .content-card, .table-container,
    div[class*="banner"], .alert-info, .jumbotron {
        background: var(--bg-glass-card) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-glass) !important;
        color: var(--text-primary) !important;
        transition: var(--sp-transition) !important;
    }

    .card:hover, .stat-card:hover {
        border-color: var(--border-glass-hover) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45) !important;
    }

    /* CONTEÚDO PRINCIPAL */
    .main-content, .content-wrapper, main {
        background: transparent !important;
    }

    /* TIPOGRAFIA & HIERARQUIA */
    h1, h2, h3, h4, h5, h6, .card-title, .heading, strong, b {
        color: var(--text-primary) !important;
    }

    p, span, label, li, td {
        color: var(--text-primary) !important;
    }

    .text-muted, small, .subtitle, .meta-text {
        color: var(--text-secondary) !important;
    }

    /* TABELAS MODERNAS TRANSLÚCIDAS */
    table, .table {
        background: transparent !important;
        color: var(--text-primary) !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }

    table th, .table th {
        background: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--border-glass) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }

    table td, .table td {
        background: transparent !important;
        border-bottom: 1px solid var(--border-glass) !important;
        color: var(--text-primary) !important;
    }

    table tr:hover td, .table tr:hover td {
        background: var(--table-row-hover) !important;
    }

    /* INPUTS, BUSCA & SELECTS */
    input, select, textarea {
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        transition: var(--sp-transition) !important;
    }

    input:focus, select:focus, textarea:focus {
        border-color: var(--sp-cyan) !important;
        box-shadow: 0 0 0 3px rgba(0, 174, 239, 0.25) !important;
        outline: none !important;
    }

    input::placeholder {
        color: var(--text-muted) !important;
    }

    /* BOTÃO DE TEMA CAPSULE */
    .btn-theme-toggle {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--input-bg);
        border: 1px solid var(--border-glass-hover);
        color: var(--text-primary);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: var(--sp-transition);
        user-select: none;
    }

    .btn-theme-toggle:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: var(--sp-cyan);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 174, 239, 0.2);
    }
    `;

    function aplicarEstilos() {
        let styleTag = document.getElementById('spaguas-glassmorphism-theme');
        if (!styleTag) {
            styleTag = document.createElement('style');
            styleTag.id = 'spaguas-glassmorphism-theme';
            document.head.appendChild(styleTag);
        }
        styleTag.textContent = cssGlassmorphism;
    }

    // 2. CONTROLE DO TEMA (DARK / LIGHT)
    function definirTema(tema) {
        document.documentElement.setAttribute('data-theme', tema);
        document.body.setAttribute('data-theme', tema);
        localStorage.setItem('cockpit_theme', tema);
        atualizarBotaoTema(tema);
    }

    function toggleTema() {
        const temaAtual = document.documentElement.getAttribute('data-theme') || 'dark';
        const novoTema = temaAtual === 'dark' ? 'light' : 'dark';
        definirTema(novoTema);
    }

    function atualizarBotaoTema(tema) {
        const btn = document.getElementById('btn-toggle-theme');
        if (btn) {
            if (tema === 'dark') {
                btn.innerHTML = '🌙 <span>Dark</span>';
                btn.title = 'Alternar para Modo Claro';
            } else {
                btn.innerHTML = '☀️ <span>Light</span>';
                btn.title = 'Alternar para Modo Escuro';
            }
        }
    }

    // 3. TELEMETRIA DOS 5 LEDS & TOPBAR
    async function checarStatusServico(url, timeoutMs = 2500) {
        try {
            const controller = new AbortController();
            const idTimeout = setTimeout(() => controller.abort(), timeoutMs);
            const resp = await fetch(url, { signal: controller.signal, cache: 'no-store' });
            clearTimeout(idTimeout);
            return resp.ok;
        } catch (e) {
            return false;
        }
    }

    async function atualizarTelemetria() {
        const sMariaDB = await checarStatusServico('/api/v1/mariadb/status');
        const sOllama = await checarStatusServico('/api/v1/ia/status');
        const sGlpi = await checarStatusServico('/api/v1/glpi/status');
        const sOpenProject = await checarStatusServico('/api/v1/openproject/status');
        const sNewApi = await checarStatusServico('/api/v1/newapi/status');

        const elMariaDB = document.getElementById('led-mariadb');
        const elOllama = document.getElementById('led-ollama');
        const elGlpi = document.getElementById('led-glpi');
        const elOp = document.getElementById('led-openproject');
        const elNewApi = document.getElementById('led-newapi');

        if (elMariaDB) elMariaDB.textContent = sMariaDB ? '🟢' : '🔴';
        if (elOllama) elOllama.textContent = sOllama ? '🟢' : '🔴';
        if (elGlpi) elGlpi.textContent = sGlpi ? '🟢' : '🔴';
        if (elOp) elOp.textContent = sOpenProject ? '🟢' : '🔴';
        if (elNewApi) elNewApi.textContent = sNewApi ? '🟢' : '🔴';

        const elSinc = document.getElementById('tempo-sinc');
        if (elSinc) {
            const agora = new Date();
            elSinc.textContent = agora.toLocaleTimeString('pt-BR');
        }
    }

    function montarWidgetInfraETema() {
        const topbar = document.querySelector('.topbar') || document.querySelector('header');
        if (!topbar) return;

        let containerInfra = document.getElementById('widget-infra-cockpit');
        if (!containerInfra) {
            containerInfra = document.createElement('div');
            containerInfra.id = 'widget-infra-cockpit';
            containerInfra.style.display = 'inline-flex';
            containerInfra.style.alignItems = 'center';
            containerInfra.style.gap = '10px';
            containerInfra.style.flexShrink = '0';

            containerInfra.innerHTML = `
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; font-size: 11px;">
                    <span style="font-weight: 700; letter-spacing: 0.5px;">INFRA :5000</span>
                    <span id="led-mariadb" title="MariaDB (:3306)">🟢</span>
                    <span id="led-ollama" title="Ollama (:11434)">🟢</span>
                    <span id="led-glpi" title="GLPI Produção (Read-Only)">🟢</span>
                    <span id="led-openproject" title="OpenProject Produção (Trava SA-GTI)">🟢</span>
                    <span id="led-newapi" title="New API (:3001)">🟢</span>
                    <span style="color: var(--text-muted); margin-left: 4px;">Sinc:</span>
                    <span id="tempo-sinc" style="font-weight: 600;">--:--:--</span>
                    <span id="btn-recarregar-infra" style="cursor: pointer; opacity: 0.8;" title="Recarregar Telemetria">🔄</span>
                </div>
                <button id="btn-toggle-theme" class="btn-theme-toggle" type="button" title="Alternar Modo de Cor">
                    🌙 <span>Dark</span>
                </button>
            `;

            const elRef = topbar.querySelector('.user-profile') || topbar.querySelector('select') || null;
            if (elRef) {
                topbar.insertBefore(containerInfra, elRef);
            } else {
                topbar.appendChild(containerInfra);
            }

            document.getElementById('btn-recarregar-infra')?.addEventListener('click', atualizarTelemetria);
            document.getElementById('btn-toggle-theme')?.addEventListener('click', toggleTema);
        }

        const temaSalvo = localStorage.getItem('cockpit_theme') || 'dark';
        definirTema(temaSalvo);
    }

    // 4. INICIALIZAÇÃO
    function init() {
        aplicarEstilos();
        montarWidgetInfraETema();
        atualizarTelemetria();
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

print("conector_api.js atualizado com o Motor Glassmorphism e Telemetria!")
