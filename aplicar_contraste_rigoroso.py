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

# 1. Remover o banner executivo do topo se ainda existir no HTML
header_id = 'id="executive-top-header"'
pos_h = text.find(header_id)
if pos_h != -1:
    start_h = text.rfind('<div', 0, pos_h)
    idx = start_h + 4
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
    end_h = idx
    text = text[:start_h] + text[end_h:]

# 2. Atualizar função criarDonut para Dark Mode nativo com legendas claras
old_cd = """function criarDonut(elemId, labels, series, colors) {
        const el = document.getElementById(elemId);
        if (!el) return;
        const options = {
            series: series,
            labels: labels,
            chart: { type: 'donut', height: 230 },
            colors: colors,
            legend: { position: 'bottom', fontSize: '11px', markers: { width: 8, height: 8 } },
            dataLabels: { enabled: true, formatter: val => Math.round(val) + '%' },
            plotOptions: { pie: { donut: { size: '58%' } } }
        };
        new ApexCharts(el, options).render();
    }"""

new_cd = """function criarDonut(elemId, labels, series, colors) {
        const el = document.getElementById(elemId);
        if (!el) return;
        const options = {
            series: series,
            labels: labels,
            theme: { mode: 'dark' },
            chart: { type: 'donut', height: 230, foreColor: '#cbd5e1', background: 'transparent' },
            colors: colors,
            legend: { position: 'bottom', fontSize: '11.5px', labels: { colors: '#cbd5e1' }, markers: { width: 8, height: 8 } },
            dataLabels: { enabled: true, style: { fontSize: '12px', fontWeight: '800', colors: ['#ffffff'] }, formatter: val => Math.round(val) + '%' },
            plotOptions: { pie: { donut: { size: '58%' } } }
        };
        new ApexCharts(el, options).render();
    }"""

if old_cd in text:
    text = text.replace(old_cd, new_cd)

# 3. Aplicar Regras Definitivas de Alto Contraste
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

    /* 1. ELIMINAR BANNERS SUPERIORES COMPLETAMENTE */
    #executive-top-header,
    .page-banner,
    #dash-banner-principal,
    #glpi-banner-principal {
        display: none !important;
    }

    /* 2. SCROLLBARS DARK MINIMALISTAS */
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

    /* 3. SIDEBAR LIMPA & SEM SCROLLBAR */
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

    /* 4. CARDS DE MÉTRICAS (ALTO CONTRASTE) */
    .kpi-row {
        display: grid !important;
        gap: 16px !important;
        margin-bottom: 22px !important;
    }

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

    .kpi-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.45) !important;
    }

    .kpi-card .kpi-val,
    .kpi-card div[style*="font-size:32px"],
    .kpi-card div[style*="font-size: 32px"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 32px !important;
        line-height: 1.1 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
    }

    .kpi-card .kpi-title,
    .kpi-card div[style*="font-weight:700"],
    .kpi-card div[style*="font-weight: 700"] {
        color: #cbd5e1 !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
    }

    .kpi-card span,
    .kpi-card small,
    .kpi-card span[style*="color:#64748b"],
    .kpi-card span[style*="color:#bfdbfe"] {
        color: #94a3b8 !important;
        font-size: 11px !important;
    }

    /* 5. OS 3 CARDS DO TRACKS SA-GTI (#view-tracks_sagti) */
    #view-tracks_sagti .table-card[style*="border-left"],
    #view-tracks_sagti .table-card {
        background: rgba(15, 23, 42, 0.78) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.35) !important;
        padding: 18px 20px !important;
    }

    #view-tracks_sagti .table-card div[style*="font-size:14px"],
    #view-tracks_sagti .table-card div[style*="font-size: 14px"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        margin-bottom: 8px !important;
    }

    #view-tracks_sagti .table-card p {
        color: #cbd5e1 !important;
        line-height: 1.5 !important;
    }

    #view-tracks_sagti .table-card div[style*="Lastro"],
    #view-tracks_sagti .table-card div[style*="background:#e0f2fe"],
    #view-tracks_sagti .table-card div[style*="background:#dbeafe"],
    #view-tracks_sagti .table-card div[style*="background:#ede9fe"] {
        background: rgba(14, 165, 233, 0.16) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    /* 6. OS 8 CARDS DE KPIS DO PDTIC (#grid-kpis-pdtic-oficial) */
    #grid-kpis-pdtic-oficial > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-left: 4px solid #38bdf8 !important;
        border-radius: 14px !important;
        padding: 12px 14px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
    }

    #grid-kpis-pdtic-oficial > div > div:nth-child(1) {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        font-size: 10.5px !important;
        letter-spacing: 0.5px !important;
    }

    #grid-kpis-pdtic-oficial > div > div:nth-child(2) {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        margin: 6px 0 !important;
    }

    #grid-kpis-pdtic-oficial > div > div:nth-child(3) {
        color: #94a3b8 !important;
        font-size: 11px !important;
        line-height: 1.4 !important;
    }

    /* 7. CONTRASTE GLOBAL PARA TÍTULOS DE SEÇÃO */
    div[style*="color:#0f2d59"],
    div[style*="color: #0f2d59"],
    span[style*="color:#0f2d59"],
    strong[style*="color:#0f2d59"],
    div[style*="color:#002d5a"],
    h3[style*="color:#002d5a"],
    div[style*="color:#1e293b"],
    div[style*="color:#334155"],
    div[style*="color:#1e1b4b"],
    span[style*="color:#1e1b4b"],
    .table-header-title {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px !important;
    }

    div[style*="color:#475569"],
    span[style*="color:#475569"],
    div[style*="color:#64748b"],
    span[style*="color:#64748b"] {
        color: #94a3b8 !important;
    }

    div[style*="color:#0369a1"],
    span[style*="color:#0369a1"],
    div[style*="color:#0284c7"],
    span[style*="color:#0284c7"],
    span[style*="color:#4f46e5"] {
        color: #38bdf8 !important;
    }

    /* 8. CONTRASTE EM TODAS AS TABELAS */
    .table-card {
        background: rgba(15, 23, 42, 0.75) !important;
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
        background: rgba(15, 23, 42, 0.95) !important;
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
    table tbody tr[style*="background:#f0fdf4"],
    table tbody tr[style*="background: #f0fdf4"],
    table tbody tr {
        background: transparent !important;
    }
    table tr:hover td {
        background: rgba(30, 41, 59, 0.7) !important;
    }
    table td a,
    table td a span,
    table td strong,
    table td[style*="monospace"] {
        color: #38bdf8 !important;
        text-decoration: none !important;
        font-weight: 700 !important;
    }

    table td span[style*="background:#dbeafe"],
    table td span[style*="background:#ede9fe"],
    table td span[style*="background:#dcfce7"],
    table td span[style*="background: #dbeafe"],
    table td span[style*="background: #ede9fe"],
    table td span[style*="background: #dcfce7"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 6px !important;
    }

    /* 9. CONTRASTE NOS GRÁFICOS APEXCHARTS */
    .apexcharts-legend-text {
        color: #cbd5e1 !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
    }
    .apexcharts-datalabel,
    .apexcharts-pie-label,
    text.apexcharts-text {
        fill: #ffffff !important;
        font-weight: 800 !important;
    }
    .apexcharts-text tspan {
        fill: #cbd5e1 !important;
    }
    .apexcharts-yaxis-label,
    .apexcharts-xaxis-label,
    text.apexcharts-yaxis-label,
    text.apexcharts-xaxis-label {
        fill: #cbd5e1 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    .apexcharts-gridline {
        stroke: rgba(255, 255, 255, 0.08) !important;
    }

    .chart-card {
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35) !important;
        overflow: hidden !important;
    }
    .chart-header {
        background: rgba(255, 255, 255, 0.04) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* 10. FORMULÁRIOS, LABELS & DROPDOWNS */
    label,
    .form-label,
    label[style*="color:#475569"],
    label[style*="color:#64748b"] {
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase !important;
    }

    select,
    input[type="text"],
    select[style*="color:#002d5a"],
    input[style*="color:#002d5a"] {
        background: rgba(15, 23, 42, 0.85) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        font-size: 12px !important;
    }
    select option {
        background: #0f172a !important;
        color: #ffffff !important;
    }
    input::placeholder {
        color: #64748b !important;
    }

    /* 11. CONTÊINERES CLAROS & PÍLULAS */
    div[style*="background: white"],
    div[style*="background:white"],
    div[style*="background: #ffffff"],
    div[style*="background:#ffffff"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
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

print("✅ Alto contraste rigoroso aplicado em Tracks, PDTIC e GLPI!")
print(f"📁 Arquivo atualizado: {target}")
