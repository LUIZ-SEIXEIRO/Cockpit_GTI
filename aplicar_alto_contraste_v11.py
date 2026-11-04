import os

caminhos = [
    r"C:\Cockpit_GTI\frontend\painel.html",
    r"frontend\painel.html",
    "painel.html"
]

target = None
for c in caminhos:
    if os.path.exists(c):
        target = c
        break

if not target:
    print("❌ Arquivo painel.html não encontrado!")
    exit(1)

with open(target, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Atualizar switchTab para manter o Eixo Pai ativo na sidebar
old_switch = """document.querySelectorAll('#sidebar .nav-item').forEach(function(el) {
        if (el.getAttribute('data-tab') === tabId) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });"""

new_switch = """var eixosParentMap = {
        'dashboards': 'dashboards',
        'visao_estrategica': 'dashboards',
        'portfolio_openproject': 'dashboards',
        'tracks_sagti': 'dashboards',
        'pdtic_eixos': 'dashboards',
        'gestao_glpi': 'dashboards',
        'mesa_trabalho': 'mesa_trabalho',
        'consulta': 'mesa_trabalho',
        'fixados': 'mesa_trabalho',
        'daily_warroom': 'daily_warroom',
        'gestao_agil': 'daily_warroom',
        'auditoria': 'daily_warroom',
        'configuracoes': 'configuracoes',
        'esteira_ia': 'configuracoes',
        'cadernos': 'configuracoes'
    };
    var activeEixo = eixosParentMap[tabId] || tabId;

    document.querySelectorAll('#sidebar .nav-item').forEach(function(el) {
        if (el.getAttribute('data-tab') === activeEixo || el.getAttribute('data-tab') === tabId) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });"""

if old_switch in text:
    text = text.replace(old_switch, new_switch)

# 2. Injetar Regras de Alto Contraste e Cards Estilo Crypto Dashboard
new_style = """<style id="crypto-executive-theme">
    /* ==========================================================
       CRYPTO / FINTECH DARK EXECUTIVE DESIGN SYSTEM (V11)
       Alinhamento Estrito à Referência Visual & Alto Contraste
       ========================================================== */
    :root {
        --crypto-bg: #070a12;
        --crypto-sidebar: #090d16;
        --crypto-card: rgba(15, 23, 42, 0.75);
        --crypto-card-hover: rgba(22, 32, 54, 0.88);
        --crypto-border: 1px solid rgba(255, 255, 255, 0.08);
        --crypto-radius: 18px;
        --crypto-accent-blue: #0ea5e9;
        --crypto-accent-cyan: #38bdf8;
        --crypto-accent-emerald: #10b981;
        --crypto-accent-amber: #f59e0b;
        --crypto-text-title: #ffffff;
        --crypto-text-sub: #94a3b8;
    }

    /* 1. SCROLLBARS DARK MINIMALISTAS */
    * {
        scrollbar-width: thin !important;
        scrollbar-color: rgba(255, 255, 255, 0.16) transparent !important;
    }
    ::-webkit-scrollbar {
        width: 5px !important;
        height: 5px !important;
    }
    ::-webkit-scrollbar-track {
        background: transparent !important;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.16) !important;
        border-radius: 6px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.45) !important;
    }

    /* 2. SIDEBAR LIMPA & SEM SCROLLBAR */
    #sidebar {
        background: var(--crypto-sidebar) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
        overflow-y: hidden !important;
    }
    #sidebar .sidebar-menu {
        overflow-y: auto !important;
        scrollbar-width: none !important;
    }
    #sidebar .sidebar-menu::-webkit-scrollbar {
        display: none !important;
    }
    #sidebar .menu-category {
        display: none !important;
    }

    #sidebar .nav-item[data-tab="portfolio_openproject"],
    #sidebar .nav-item[data-tab="tracks_sagti"],
    #sidebar .nav-item[data-tab="pdtic_eixos"],
    #sidebar .nav-item[data-tab="gestao_glpi"],
    #sidebar .nav-item[data-tab="visao_estrategica"],
    #sidebar .nav-item[data-tab="gestao_agil"],
    #sidebar .nav-item[data-tab="consulta"],
    #sidebar .nav-item[data-tab="fixados"],
    #sidebar .nav-item[data-tab="auditoria"],
    #sidebar .nav-item[data-tab="esteira_ia"],
    #sidebar .nav-item[data-tab="cadernos"] {
        display: none !important;
    }

    #sidebar .nav-item {
        border-radius: 12px !important;
        padding: 12px 14px !important;
        margin-bottom: 6px !important;
        color: #8a99ad !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }

    #sidebar .nav-item:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #ffffff !important;
        transform: translateX(3px);
    }

    #sidebar .nav-item.active {
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 18px rgba(14, 165, 233, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }

    #sidebar .nav-item.active .nav-badge {
        background: rgba(255, 255, 255, 0.25) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    #sidebar .nav-item:not(.active) .nav-badge {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #8a99ad !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 3. HEADER SUPERIOR EXECUTIVO COMPACTO */
    #executive-top-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* 4. CARDS DE MÉTRICAS ESTILO CRYPTO DASHBOARD (ALTO CONTRASTE) */
    .kpi-row {
        display: grid !important;
        gap: 16px !important;
        margin-bottom: 22px !important;
    }

    #view-gestao_glpi .kpi-card,
    .kpi-card {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 18px !important;
        padding: 18px 20px !important;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.35) !important;
        border-left: 1px solid rgba(255, 255, 255, 0.09) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        min-height: 105px !important;
        transition: all 0.25s ease !important;
    }

    #view-gestao_glpi .kpi-card:hover,
    .kpi-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.45) !important;
    }

    .kpi-card .kpi-val,
    #view-gestao_glpi .kpi-val,
    .kpi-card div[style*="font-size:32px"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 32px !important;
        line-height: 1.1 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
    }

    #view-gestao_glpi .kpi-card div[style*="font-weight:700"],
    .kpi-card div[style*="font-weight:700"],
    .kpi-card .kpi-title {
        color: #cbd5e1 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
        letter-spacing: 0.3px !important;
    }

    .kpi-card.hero {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(15, 23, 42, 0.85) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        box-shadow: 0 8px 28px rgba(2, 132, 199, 0.25) !important;
    }

    .kpi-card.hero .kpi-val {
        color: #38bdf8 !important;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.5) !important;
    }

    #view-gestao_glpi .kpi-card span[style*="font-size:24px"] {
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.5)) !important;
    }

    /* 5. TÍTULOS DE SEÇÃO COM ALTO CONTRASTE */
    div[style*="color:#0f2d59"],
    span[style*="color:#0f2d59"],
    strong[style*="color:#0f2d59"],
    h3[style*="color:#0f2d59"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: 0.4px !important;
    }

    #glpi-banner-desc,
    span[style*="color:#0369a1"],
    div[style*="color:#0369a1"] {
        color: #38bdf8 !important;
    }

    div[style*="color:#475569"],
    span[style*="color:#475569"],
    div[style*="color:#1e293b"] {
        color: #cbd5e1 !important;
    }

    div[style*="color:#991b1b"],
    span[style*="color:#991b1b"],
    #glpi-real-problemas {
        color: #f87171 !important;
    }

    /* 6. TABELAS DE CHAMADOS E PROCESSOS */
    .table-card {
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        overflow: hidden !important;
    }

    .table-header-bar {
        background: rgba(255, 255, 255, 0.03) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 14px 18px !important;
    }

    table th {
        background: rgba(15, 23, 42, 0.9) !important;
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 12px 14px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    table td {
        background: rgba(15, 23, 42, 0.5) !important;
        color: #e2e8f0 !important;
        padding: 12px 14px !important;
        font-size: 12.5px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    table tr:hover td {
        background: rgba(30, 41, 59, 0.7) !important;
    }

    table td a,
    table td a span,
    table td strong {
        color: #38bdf8 !important;
        text-decoration: none !important;
        font-weight: 700 !important;
    }

    /* 7. REMOÇÃO DE CONTÊINERES CLAROS & FILTROS */
    div[style*="background: white"],
    div[style*="background:white"],
    div[style*="background: #ffffff"],
    div[style*="background:#ffffff"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
    }

    select, input[type="text"] {
        color: #ffffff !important;
    }
    select option {
        background: #0f172a !important;
        color: #ffffff !important;
    }

    .subaba-eixo1-btn, .pill-filtro-dash, .pill-filtro-farol, .pill-cfg {
        border-radius: 9999px !important;
        padding: 6px 15px !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .subaba-eixo1-btn.active, .pill-filtro-dash.active, .pill-filtro-farol.active, .pill-cfg.active,
    .btn-primary.subaba-eixo1-btn, .btn-primary.pill-filtro-farol, .btn-primary.pill-filtro-dash {
        background: rgba(14, 165, 233, 0.2) !important;
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.25) !important;
    }

    .subaba-eixo1-btn:not(.active), .pill-filtro-dash:not(.active), .pill-filtro-farol:not(.active), .pill-cfg:not(.active),
    .btn-secondary.subaba-eixo1-btn, .btn-secondary.pill-filtro-farol, .btn-secondary.pill-filtro-dash {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #8a99ad !important;
    }

    .subaba-eixo1-btn:hover, .pill-filtro-dash:hover, .pill-filtro-farol:hover, .pill-cfg:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
    }
</style>"""

if '<style id="crypto-executive-theme">' in text:
    p1 = text.find('<style id="crypto-executive-theme">')
    p2 = text.find('</style>', p1) + len('</style>')
    text = text[:p1] + new_style + text[p2:]
else:
    head_pos = text.find('</head>')
    text = text[:head_pos] + new_style + '\n' + text[head_pos:]

with open(target, 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ Alto contraste e alinhamento visual aplicados com sucesso!")
print(f"📁 Arquivo atualizado: {target}")
