import re

target = r"C:\Cockpit_GTI\frontend\painel.html"
with open(target, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# 1. Regra CSS segura para enxugar a Sidebar nas 4 Visões Mestras
css_sidebar_enxuta = """
<style id="css-sidebar-4-visoes">
    /* EIXO 1: Manter apenas o Dashboard 360° e ocultar sub-itens na lateral */
    .nav-item[data-tab="visao_estrategica"],
    .nav-item[data-tab="portfolio_openproject"],
    .nav-item[data-tab="tracks_sagti"],
    .nav-item[data-tab="pdtic_eixos"],
    .nav-item[data-tab="gestao_glpi"] {
        display: none !important;
    }

    /* EIXO 2: Manter apenas a Mesa de Trabalho e centralizar o restante dentro dela */
    .nav-item[data-tab="consulta"],
    .nav-item[data-tab="fixados"],
    .nav-item[data-tab="esteira_ia"],
    .nav-item[data-tab="cadernos"] {
        display: none !important;
    }

    /* EIXO 3: Manter a Sala de Reuniões e ocultar Auditoria da lateral */
    .nav-item[data-tab="auditoria"],
    .nav-item[data-tab="gestao_agil"] {
        display: none !important;
    }

    /* Refinamento visual dos textos das 4 Visões */
    .nav-item[data-tab="dashboards"] .nav-item-left span::after {
        content: " (Gestão à Vista)";
        font-weight: 400;
        opacity: 0.8;
    }
    .nav-item[data-tab="mesa_trabalho"] .nav-item-left span::after {
        content: " (Hub Operacional)";
        font-weight: 400;
        opacity: 0.8;
    }
    .nav-item[data-tab="daily_warroom"] .nav-item-left span::after {
        content: " & Diretoria";
        font-weight: 400;
        opacity: 0.8;
    }

    /* Barra Integrada da Mesa de Trabalho (Eixo 2) */
    .mesa-toolbar-integrada {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin-bottom: 20px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
    }
</style>
"""

html = re.sub(r'<style id="css-sidebar-4-visoes">[\s\S]*?</style>', '', html)

if "</head>" in html:
    html = html.replace("</head>", css_sidebar_enxuta + "\n</head>", 1)
else:
    html = css_sidebar_enxuta + "\n" + html

# 2. Injetar a Barra de Ferramentas dentro da Mesa de Trabalho
barra_mesa = """
            <!-- BARRA DE FERRAMENTAS INTEGRADA NA MESA DE TRABALHO (EIXO 2) -->
            <div class="mesa-toolbar-integrada">
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 12px; font-weight: 800; color: #ffffff; margin-right: 6px;">📂 Acesso Rápido:</span>
                    <button class="btn btn-primary" onclick="switchTab('mesa_trabalho')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 700;">📌 Minha Custódia (Luiz)</button>
                    <button class="btn btn-secondary" onclick="switchTab('fixados')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">⭐ Fixados</button>
                    <button class="btn btn-secondary" onclick="switchTab('consulta')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">📁 Acervo SEI (197)</button>
                    <button class="btn btn-secondary" onclick="switchTab('tracks_sagti')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">📦 OpenProject (97)</button>
                </div>
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="switchTab('consulta'); var b = document.getElementById('btn-upload-sei-topo') || document.querySelector('button[onclick*=\'upload\']'); if(b) b.click();" style="background: #01a75f; border-color: #01a75f; font-weight: 700; padding: 6px 14px; font-size: 11.5px;">
                        📥 Upload PDF SEI (v7.1)
                    </button>
                    <button class="btn btn-secondary" onclick="switchTab('esteira_ia')" style="background: rgba(99,102,241,0.25); border-color: rgba(129,140,248,0.5); color: #e0e7ff; font-weight: 700; padding: 6px 12px; font-size: 11.5px;">
                        🤖 Copiloto IA & RACI
                    </button>
                    <button class="btn btn-secondary" onclick="switchTab('cadernos')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">
                        📄 Toolkits A4 (Lei 14.133)
                    </button>
                </div>
            </div>
"""

# Remover barra antiga se houver e injetar no início da view-mesa_trabalho
html = re.sub(r'<!-- BARRA DE FERRAMENTAS INTEGRADA NA MESA DE TRABALHO[\s\S]*?</div>\s*</div>', '', html)

if '<div id="view-mesa_trabalho" class="tab-view">' in html:
    html = html.replace(
        '<div id="view-mesa_trabalho" class="tab-view">',
        '<div id="view-mesa_trabalho" class="tab-view">\n' + barra_mesa,
        1
    )

with open(target, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)

print("✅ Sidebar enxuta nas 4 Visões e Barra Integrada da Mesa de Trabalho aplicadas com sucesso!")
