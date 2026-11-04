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

# 1. Injetar CSS do Design System (se ainda não existir)
if 'CRYPTO / FINTECH DARK EXECUTIVE DESIGN SYSTEM' not in text:
    css_to_add = """
    /* ==========================================================
       CRYPTO / FINTECH DARK EXECUTIVE DESIGN SYSTEM (V11)
       Inspirado na referência visual executiva
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

    #sidebar .nav-item {
        border-radius: 12px !important;
        padding: 11px 14px !important;
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
"""
    head_pos = text.find('</head>')
    text = text[:head_pos] + css_to_add + '\n' + text[head_pos:]

# 2. Injetar Top Header Executivo no topo de .content-scroll (se não existir)
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
                    <!-- Busca Estilo Pílula da Imagem -->
                    <div style="display: flex; align-items: center; gap: 8px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 9999px; padding: 7px 16px; width: 280px; backdrop-filter: blur(12px); box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);">
                        <span style="color: #64748b; font-size: 13px;">🔍</span>
                        <input type="text" id="global-header-search" placeholder="Buscar no Cockpit (Ctrl+K)..." onkeydown="if(event.key==='Enter'){if(window.dispararBuscaGlobal)window.dispararBuscaGlobal(this.value);}" style="border: none; background: transparent; color: #fff; font-size: 11.5px; outline: none; width: 100%;">
                    </div>

                    <!-- Notificações -->
                    <div style="position: relative; width: 36px; height: 36px; border-radius: 50%; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; align-items: center; justify-content: center; cursor: pointer; color: #94a3b8; transition: all 0.2s ease;" title="Alertas do Cockpit">
                        <span style="font-size: 15px;">🔔</span>
                        <span style="position: absolute; top: 7px; right: 7px; width: 7px; height: 7px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 8px #38bdf8;"></span>
                    </div>

                    <!-- Chip do Usuário -->
                    <div style="display: flex; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); padding: 3px 12px 3px 4px; border-radius: 9999px;">
                        <div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #00a859 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 11px; color: #fff; box-shadow: 0 2px 6px rgba(2,132,199,0.4);">
                            LS
                        </div>
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

print("✅ Etapa 1 aplicada com sucesso!")
print(f"📁 Arquivo atualizado: {target} (Tags balanceadas: {o})")
