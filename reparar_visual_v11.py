import os
import re

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

# 1. Remover qualquer texto de CSS solto ou tags de tema antigas
kw = 'CRYPTO / FINTECH DARK EXECUTIVE DESIGN SYSTEM'
p = text.find(kw)
while p != -1:
    style_start = text.rfind('<style', 0, p)
    style_end = text.find('</style>', style_start)
    if style_start != -1 and style_end > p:
        text = text[:style_start] + text[style_end + len('</style>'):]
    else:
        comment_start = text.rfind('/*', 0, p)
        if comment_start == -1: comment_start = p
        tag_end = text.find('</head>', p)
        if tag_end != -1:
            text = text[:comment_start] + text[tag_end:]
        else:
            tag_end = text.find('<', p)
            text = text[:comment_start] + text[tag_end:]
    p = text.find(kw)

# 2. Injetar o CSS envelopado estritamente em <style>
css_block = """<style id="crypto-executive-theme">
    /* ==========================================================
       CRYPTO / FINTECH DARK EXECUTIVE DESIGN SYSTEM (V11)
       ========================================================== */
    :root {
        --crypto-bg: #070a12;
        --crypto-sidebar: #090d16;
        --crypto-card: rgba(15, 23, 42, 0.72);
        --crypto-card-hover: rgba(22, 32, 54, 0.85);
        --crypto-border: 1px solid rgba(255, 255, 255, 0.08);
        --crypto-radius: 18px;
        --crypto-accent-blue: #0ea5e9;
        --crypto-accent-cyan: #38bdf8;
        --crypto-accent-emerald: #10b981;
        --crypto-accent-amber: #f59e0b;
        --crypto-text-title: #ffffff;
        --crypto-text-sub: #8a99ad;
    }

    #sidebar {
        background: var(--crypto-sidebar) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }

    #sidebar .menu-category {
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

    #executive-top-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 22px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .subaba-eixo1-btn, .pill-filtro-dash, .pill-cfg {
        border-radius: 9999px !important;
        padding: 7px 16px !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .subaba-eixo1-btn.active, .pill-filtro-dash.active, .pill-cfg.active,
    .btn-primary.subaba-eixo1-btn {
        background: rgba(14, 165, 233, 0.2) !important;
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.25) !important;
    }

    .subaba-eixo1-btn:not(.active), .pill-filtro-dash:not(.active), .pill-cfg:not(.active),
    .btn-secondary.subaba-eixo1-btn {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #8a99ad !important;
    }

    .subaba-eixo1-btn:hover, .pill-filtro-dash:hover, .pill-cfg:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
    }
</style>"""

head_pos = text.find('</head>')
text = text[:head_pos] + css_block + '\n' + text[head_pos:]

# 3. Atualizar Sidebar limpa (sem títulos redundantes de categorias)
clean_sidebar = """<div id="sidebar">
        <!-- 1. IDENTIDADE INSTITUCIONAL MODERNIZADA -->
        <div class="sidebar-brand" style="display: flex; align-items: center; justify-content: space-between; padding: 18px 14px 14px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.07);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(56, 189, 248, 0.35); box-shadow: 0 0 16px rgba(5, 68, 207, 0.3), inset 0 1px 0 rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); flex-shrink: 0;">
                    <img src="" data-spaguas-logo="1" alt="SP-Águas" style="height: 22px; width: auto; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">
                </div>
                <div class="brand-text">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 16px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px;">SP-Águas</span>
                        <span style="font-size: 9px; font-weight: 800; background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 1px 6px; border-radius: 6px; text-transform: uppercase;">v11</span>
                    </div>
                    <p style="font-size: 10.5px; color: #94a3b8; font-weight: 600; margin: 2px 0 0 0;">SA-GTI • Governança Digital</p>
                </div>
            </div>
            <button class="btn-toggle-sidebar" id="btn-collapse-sidebar" onclick="toggleSidebar()" title="Recolher/Expandir menu lateral" style="width: 26px; height: 26px; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #94a3b8; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 11px; transition: all 0.2s ease;">◀</button>
        </div>

        <!-- 2. BUSCA GLOBAL 360° NA SIDEBAR -->
        <div style="padding: 12px 12px 8px 12px;">
            <div style="position: relative; display: flex; align-items: center;">
                <input type="text" id="sidebar-search-input" placeholder="🔍 Busca 360° (Ctrl+K)..." onkeydown="if(event.key==='Enter'){if(window.dispararBuscaGlobal)window.dispararBuscaGlobal(this.value);}" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(255, 255, 255, 0.05); color: #fff; font-size: 11.5px; outline: none; box-sizing: border-box; transition: all 0.2s ease;">
            </div>
        </div>

        <!-- 3. NAVEGAÇÃO DOS 4 EIXOS ESTRATÉGICOS (DIRETA & LIMPA) -->
        <div class="sidebar-menu" style="flex: 1; overflow-y: auto; padding: 6px 10px; display: flex; flex-direction: column; gap: 5px;">
            <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">📺</span>
                    <span style="font-weight: 700;">1. Gestão à Vista 360°</span>
                </div>
                <span class="nav-badge" style="background: rgba(255,255,255,0.2); color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">360°</span>
            </div>

            <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">💼</span>
                    <span style="font-weight: 700;">2. Mesa de Trabalho &amp; IA</span>
                </div>
                <span class="nav-badge" style="background: #00a859; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Hub</span>
            </div>

            <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">🤝</span>
                    <span style="font-weight: 700;">3. Sala de Reuniões &amp; Atas</span>
                </div>
                <span class="nav-badge" style="background: #0284c7; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">15m</span>
            </div>

            <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">⚙️</span>
                    <span style="font-weight: 700;">4. Central de Configurações</span>
                </div>
                <span class="nav-badge" style="background: #475569; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Admin</span>
            </div>
        </div>

        <!-- 4. SESSÃO DO USUÁRIO & TELEMETRIA (100% DARK MODE EXCLUSIVO) -->
        <div id="sidebar-user-footer" style="padding: 14px 12px; border-top: 1px solid rgba(255, 255, 255, 0.08); background: rgba(11, 15, 25, 0.95); display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #0544cf 0%, #00a859 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px; color: #fff; flex-shrink: 0; box-shadow: 0 2px 8px rgba(5,68,207,0.35);">
                    LS
                </div>
                <div style="flex: 1; overflow: hidden; line-height: 1.25;">
                    <div style="font-size: 12.5px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Luiz Seixeiro</div>
                    <div style="font-size: 10.5px; color: #94a3b8; display: flex; align-items: center; gap: 4px;">
                        <span style="color: #facc15;">👑</span> Super-Admin
                    </div>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 5px 8px;">
                <span style="font-size: 11px;">🏛️</span>
                <select id="select-diretoria-spaguas" onchange="window.filtrarPorDiretoriaSpAguas(this.value)" style="border: none; background: transparent; font-size: 11px; font-weight: 600; color: #e2e8f0; width: 100%; outline: none; cursor: pointer;">
                    <option value="todas" style="background: #0f172a; color: #fff;">Toda a SP-Águas (Consolidado)</option>
                    <option value="spaguas-sh" style="background: #0f172a; color: #fff;">[SH] Segurança Hídrica</option>
                    <option value="spaguas-sd" style="background: #0f172a; color: #fff;">[SD] Descentralizadas</option>
                    <option value="spaguas-sr" style="background: #0f172a; color: #fff;">[SR] Regulação</option>
                    <option value="spaguas-sf" style="background: #0f172a; color: #fff;">[SF] Fiscalização</option>
                    <option value="spaguas-sa" style="background: #0f172a; color: #fff;">[SA] Administrativa</option>
                    <option value="spaguas-sa-gti" style="background: #0f172a; color: #fff;">[SA-GTI] TIC Governança</option>
                </select>
            </div>

            <select id="select-perfil-ativo" onchange="window.trocarPerfilAtivo(this.value)" style="display: none;">
                <option value="Super-Admin">Super-Admin</option>
                <option value="Gestor">Gestor</option>
                <option value="Analista">Analista</option>
                <option value="Demandante">Demandante</option>
            </select>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 2px 0 2px;">
                <div id="widget-infra-sidebar" style="display: inline-flex; align-items: center; gap: 5px; font-size: 10px; color: #94a3b8; font-family: monospace;">
                    <span style="font-weight: 800; color: #4ade80; letter-spacing: 0.5px;">INFRA</span>
                    <span id="led-mariadb" title="MariaDB (:3306)">🟢</span>
                    <span id="led-ollama" title="Ollama (:11434)">🟢</span>
                    <span id="led-glpi" title="GLPI">🟢</span>
                    <span id="led-openproject" title="OpenProject">🟢</span>
                    <span id="led-newapi" title="New API (:3001)">🟢</span>
                </div>
                <span style="font-size: 9.5px; color: #64748b; font-weight: 600;">Sistemas OK</span>
            </div>
        </div>
    </div>"""

pos_side = text.find('id="sidebar"')
start_side = text.rfind('<div', 0, pos_side)
pos_main = text.find('<!-- MAIN -->')
if pos_main == -1: pos_main = text.find('id="main"')

text = text[:start_side] + clean_sidebar + '\n\n    <!-- MAIN -->\n    ' + text[pos_main:]

# 4. Inserir Top Header Executivo limpo (se não existir)
if 'id="executive-top-header"' not in text:
    header_html = """            <!-- HEADER EXECUTIVO ESTILO CRYPTO DASHBOARD ("Welcome Back, John!") -->
            <div id="executive-top-header">
                <div>
                    <h1 style="font-size: 22px; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px;">
                        Painel de Governança, <span style="background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Luiz!</span>
                    </h1>
                    <p style="font-size: 11.5px; color: #8a99ad; margin: 3px 0 0 0; font-weight: 500;">
                        Monitoramento Estratégico em Tempo Real • SP-Águas SA-GTI
                    </p>
                </div>

                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="display: flex; align-items: center; gap: 8px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 9999px; padding: 7px 16px; width: 280px; backdrop-filter: blur(12px); box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);">
                        <span style="color: #64748b; font-size: 13px;">🔍</span>
                        <input type="text" id="global-header-search" placeholder="Buscar no Cockpit (Ctrl+K)..." onkeydown="if(event.key==='Enter'){if(window.dispararBuscaGlobal)window.dispararBuscaGlobal(this.value);}" style="border: none; background: transparent; color: #fff; font-size: 11.5px; outline: none; width: 100%;">
                    </div>

                    <div style="position: relative; width: 36px; height: 36px; border-radius: 50%; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; align-items: center; justify-content: center; cursor: pointer; color: #94a3b8; transition: all 0.2s ease;" title="Alertas do Cockpit">
                        <span style="font-size: 15px;">🔔</span>
                        <span style="position: absolute; top: 7px; right: 7px; width: 7px; height: 7px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 8px #38bdf8;"></span>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); padding: 3px 12px 3px 4px; border-radius: 9999px;">
                        <div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #00a859 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 11px; color: #fff; box-shadow: 0 2px 6px rgba(2,132,199,0.4);">LS</div>
                        <div style="line-height: 1.2;">
                            <div style="font-size: 11.5px; font-weight: 700; color: #fff;">Luiz Seixeiro</div>
                            <div style="font-size: 9.5px; color: #38bdf8; font-weight: 600;">Super-Admin</div>
                        </div>
                    </div>
                </div>
            </div>"""
    target_div = '<div class="content-scroll">'
    cs_pos = text.find(target_div)
    if cs_pos != -1:
        text = text[:cs_pos + len(target_div)] + '\n' + header_html + text[cs_pos + len(target_div):]

o = text.count('<div')
c = text.count('</div')
if o != c:
    print(f"❌ Erro de integridade: open={o}, close={c}")
    exit(1)

with open(target, 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ Correção definitiva aplicada com sucesso!")
print(f"📁 Arquivo atualizado: {target} (Tags balanceadas: {o})")
