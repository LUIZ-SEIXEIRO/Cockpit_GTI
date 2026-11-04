import os
import shutil
import re

print("🚀 Iniciando implantação da Fase 3: Sidebar Unificada, Fim do Banner & 4 Visões Mestras...")

painel_path = r"C:\Cockpit_GTI\frontend\painel.html"
backup_path = painel_path + ".bak_fase3"
shutil.copy(painel_path, backup_path)
print(f"📦 Backup de segurança criado: {backup_path}")

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# 1. CSS de Estilização da Fase 3 (Ocultação de Banners e Topbar + Glassmorphism Total)
css_fase3 = """
<!-- ======================================================== -->
<!-- ESTILOS FASE 3: SIDEBAR UNIFICADA, 4 EIXOS & FIM DO BANNER -->
<!-- ======================================================== -->
<style id="estilos-fase3-unificada">
    /* 1. Ocultação total do Topbar e de todos os Banners Azuis Antigos */
    #topbar, .top-header, .page-banner, #dash-banner-principal {
        display: none !important;
    }

    #main {
        padding-top: 0 !important;
        background: transparent !important;
        overflow: hidden !important;
    }

    .content-scroll {
        padding: 18px 24px 30px 24px !important;
        height: 100vh !important;
        overflow-y: auto !important;
        background: transparent !important;
    }

    /* 2. Sidebar Unificada Glassmorphism */
    #sidebar {
        background: rgba(9, 13, 22, 0.94) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        display: flex !important;
        flex-direction: column !important;
        z-index: 1000 !important;
    }

    .sidebar-brand {
        padding: 16px 14px 12px 14px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .nav-item {
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    .nav-item:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        transform: translateX(3px) !important;
    }

    .nav-item.active {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.35) 0%, rgba(37, 99, 235, 0.45) 100%) !important;
        border: 1px solid rgba(96, 165, 250, 0.4) !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.25) !important;
    }

    .nav-item.active .nav-item-left span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* 3. Cards de Scorecard no Eixo 1 (Glassmorphism Escuro com Semáforos Luminosos) */
    .kpi-row .kpi-card:not(.hero),
    .kpi-card:not(.hero) {
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.38) !important;
        color: #ffffff !important;
    }

    .kpi-card.hero {
        background: linear-gradient(135deg, rgba(5, 68, 207, 0.65) 0%, rgba(15, 23, 42, 0.88) 100%) !important;
        backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(96, 165, 250, 0.45) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
    }

    /* Pílulas de Modos do Dashboard */
    div:has(> .pill-filtro-dash) {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }

    .pill-filtro-dash.btn-primary {
        background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%) !important;
        border: 1px solid rgba(96, 165, 250, 0.5) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .pill-filtro-dash.btn-secondary {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #cbd5e1 !important;
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

# Remover estilos antigos da Fase 3 se houver e injetar antes de </head>
content = re.sub(r'<style id="estilos-fase3-unificada">[\s\S]*?</style>', '', content)
if "</head>" in content:
    content = content.replace("</head>", css_fase3 + "\n</head>", 1)
else:
    content = css_fase3 + "\n" + content

# 2. Nova Estrutura da Sidebar Unificada com as 4 Visões Mestras
nova_sidebar_html = """
        <div class="sidebar-search-box" style="padding: 10px 14px; margin-bottom: 4px;">
            <div style="position: relative; display: flex; align-items: center;">
                <input type="text" id="sidebar-global-search" placeholder="🔍 Busca 360° (Ctrl+K)..." onkeyup="if(event.key==='Enter') window.executarBuscaGlobal360(this.value)" style="width: 100%; box-sizing: border-box; padding: 8px 12px 8px 30px; background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 8px; color: #ffffff; font-size: 11.5px; outline: none;">
                <span style="position: absolute; left: 10px; font-size: 11px; color: #94a3b8; pointer-events: none;">🔍</span>
            </div>
        </div>

        <div class="sidebar-menu" style="flex: 1; overflow-y: auto;">
            <div class="menu-category" style="font-size: 10px; font-weight: 800; color: #64748b; letter-spacing: 0.8px; padding: 4px 14px 8px 14px;">VISÕES ESTRATÉGICAS (4 EIXOS)</div>
            
            <!-- EIXO 1: GESTÃO À VISTA (DASHBOARD 360°) -->
            <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                    <span style="font-size: 16px;">📺</span> <span>1. Gestão à Vista</span>
                </div>
                <span class="nav-badge" style="background: rgba(37, 99, 235, 0.3); border: 1px solid rgba(96, 165, 250, 0.4); color: #93c5fd; font-size: 10px; font-weight: 700;">360°</span>
            </div>

            <!-- EIXO 2: MESA DE TRABALHO ÚNICA (HUB OPERACIONAL) -->
            <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                    <span style="font-size: 16px;">💼</span> <span>2. Mesa de Trabalho</span>
                </div>
                <span class="nav-badge" style="background: rgba(16, 185, 129, 0.25); border: 1px solid rgba(52, 211, 153, 0.4); color: #a7f3d0; font-size: 10px; font-weight: 700;">Operação</span>
            </div>

            <!-- EIXO 3: SALA DE REUNIÕES & DIRETORIA -->
            <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                    <span style="font-size: 16px;">🤝</span> <span>3. Sala de Reuniões</span>
                </div>
                <span class="nav-badge" style="background: rgba(124, 58, 237, 0.25); border: 1px solid rgba(167, 139, 250, 0.4); color: #ddd6fe; font-size: 10px; font-weight: 700;">15m • Ata</span>
            </div>

            <!-- EIXO 4: CONFIGURAÇÕES & CONECTORES -->
            <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                    <span style="font-size: 16px;">⚙️</span> <span>4. Configurações</span>
                </div>
                <span class="nav-badge" style="background: rgba(245, 158, 11, 0.25); border: 1px solid rgba(251, 191, 36, 0.4); color: #fde68a; font-size: 10px; font-weight: 700;">Sistema</span>
            </div>
        </div>

        <!-- RODAPÉ DA SIDEBAR: DIRETORIA, STATUS, SESSÃO E TEMA -->
        <div id="sidebar-unified-footer" style="padding: 12px 14px; border-top: 1px solid rgba(255, 255, 255, 0.1); background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(14px); font-size: 11px; color: #cbd5e1;">
            <div style="margin-bottom: 8px;">
                <label style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 3px;">🏢 Diretoria Ativa:</label>
                <select id="select-diretoria-spaguas-sidebar" onchange="window.filtrarPorDiretoriaSpAguas(this.value)" style="width: 100%; box-sizing: border-box; padding: 6px 8px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; color: #ffffff; font-size: 11px; font-weight: 700; outline: none; cursor: pointer;">
                    <option value="todas" style="background: #0f172a;">🌐 Toda a SP-Águas (Consolidado)</option>
                    <option value="spaguas-sh" style="background: #0f172a;">🛡️ [SH] Segurança Hídrica</option>
                    <option value="spaguas-sd" style="background: #0f172a;">🌊 [SD] Unidades Descentralizadas</option>
                    <option value="spaguas-sr" style="background: #0f172a;">⚖️ [SR] Regulação</option>
                    <option value="spaguas-sf" style="background: #0f172a;">🔍 [SF] Fiscalização</option>
                    <option value="spaguas-sa" style="background: #0f172a;">🏛️ [SA] Administrativa</option>
                    <option value="spaguas-sa-gti" selected style="background: #0f172a;">💻 [SA-GTI] Tecnologia da Informação</option>
                </select>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 10.5px;">
                <span style="display: flex; align-items: center; gap: 5px; color: #4ade80; font-weight: 700;">
                    <span style="font-size: 9px;">🟢</span> 11/11 Conectores
                </span>
                <button type="button" id="btn-toggle-theme-sidebar" onclick="window.alternarTemaCockpit()" style="padding: 3px 9px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; color: #f1f5f9; font-size: 10.5px; font-weight: 700; cursor: pointer;">
                    🌙 Dark
                </button>
            </div>

            <div id="sidebar-user-session-card" style="padding: 8px 10px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px;">
                <div style="font-weight: 800; color: #ffffff; display: flex; align-items: center; justify-content: space-between;">
                    <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;" id="sidebar-nome-usuario-display">Luiz Seixeiro</span>
                    <button type="button" onclick="window.limparUsuarioSessao()" style="padding: 2px 6px; background: rgba(239,68,68,0.25); border: 1px solid rgba(248,113,113,0.4); border-radius: 4px; color: #fca5a5; font-size: 9.5px; font-weight: 700; cursor: pointer;" title="Encerrar sessão">🚪 Sair</button>
                </div>
                <div style="font-size: 9.5px; color: #94a3b8; margin-top: 2px;" id="sidebar-perfil-usuario-display">👑 Super-Admin (SA-GTI)</div>
            </div>
        </div>
"""

content = re.sub(r'<div class="sidebar-menu">[\s\S]*?</div>\s*</div>\s*</div>', nova_sidebar_html + '\n    </div>', content, count=1)

# 3. Injetar a Barra de Ferramentas Integrada dentro da Mesa de Trabalho (#view-mesa_trabalho)
barra_mesa_html = """
            <!-- BARRA DE FERRAMENTAS INTEGRADA NA MESA DE TRABALHO (EIXO 2) -->
            <div class="mesa-toolbar-integrada">
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 12px; font-weight: 800; color: #ffffff; margin-right: 6px;">📂 Filtros da Mesa:</span>
                    <button class="btn btn-primary" onclick="window.filtrarMesa('minhas')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 700;">📌 Minha Custódia</button>
                    <button class="btn btn-secondary" onclick="window.filtrarMesa('fixados')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">⭐ Fixados</button>
                    <button class="btn btn-secondary" onclick="window.filtrarMesa('acervo')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">📁 Acervo SEI (197)</button>
                    <button class="btn btn-secondary" onclick="window.filtrarMesa('openproject')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">📦 OpenProject (97)</button>
                </div>
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="window.abrirModalUploadSei()" style="background: #01a75f; border-color: #01a75f; font-weight: 700; padding: 6px 14px; font-size: 11.5px;">
                        📥 Upload PDF SEI (v7.1)
                    </button>
                    <button class="btn btn-secondary" onclick="window.abrirDrawerAi()" style="background: rgba(99,102,241,0.25); border-color: rgba(129,140,248,0.5); color: #e0e7ff; font-weight: 700; padding: 6px 12px; font-size: 11.5px;">
                        🤖 Copiloto IA & RACI
                    </button>
                    <button class="btn btn-secondary" onclick="switchTab('cadernos')" style="padding: 6px 12px; font-size: 11.5px; font-weight: 600;">
                        📄 Toolkits A4 (Lei 14.133)
                    </button>
                </div>
            </div>
"""

if '<div id="view-mesa_trabalho" class="tab-view">' in content:
    content = content.replace(
        '<div id="view-mesa_trabalho" class="tab-view">',
        '<div id="view-mesa_trabalho" class="tab-view">\n' + barra_mesa_html,
        1
    )

# 4. Injetar funções auxiliares no JavaScript (Busca, Filtros e Alternância de Tema)
js_fase3 = """
<script id="script-fase3-unificada">
(function() {
    window.alternarTemaCockpit = function() {
        var atual = localStorage.getItem("sagti_theme_mode") || "dark";
        var novo = (atual === "dark") ? "light" : "dark";
        localStorage.setItem("sagti_theme_mode", novo);
        
        var btn = document.getElementById("btn-toggle-theme-sidebar");
        if (btn) btn.innerText = (novo === "dark") ? "🌙 Dark" : "☀️ Light";

        if (typeof window.aplicarGlassmorphismDualTheme === "function") {
            window.aplicarGlassmorphismDualTheme(novo);
        } else {
            document.body.className = (novo === "dark") ? "theme-dark" : "theme-light";
        }
    };

    window.executarBuscaGlobal360 = function(termo) {
        if (!termo || !termo.trim()) return;
        var t = termo.trim().toLowerCase();
        
        // Se parecer número de processo SEI, abre detalhes ou busca
        if (/^\\d{3}\\./.test(t) || t.indexOf("137.") !== -1) {
            if (typeof window.abrirDetalhesProcesso === "function") {
                window.abrirDetalhesProcesso(termo.trim());
                return;
            }
        }
        
        // Direcionar para a Mesa e filtrar
        switchTab("mesa_trabalho");
        var inpBusca = document.getElementById("filtro-busca-global") || document.getElementById("input-busca-consulta");
        if (inpBusca) {
            inpBusca.value = termo.trim();
            if (typeof window.filtrarConsulta === "function") window.filtrarConsulta();
        }
    };

    window.filtrarMesa = function(modo) {
        if (modo === "acervo") {
            switchTab("consulta");
        } else if (modo === "openproject") {
            switchTab("tracks_sagti");
        } else if (modo === "fixados") {
            switchTab("fixados");
        } else {
            switchTab("mesa_trabalho");
        }
    };

    window.abrirModalUploadSei = function() {
        switchTab("consulta");
        var btnUpload = document.getElementById("btn-upload-sei-topo") || document.querySelector("button[onclick*='upload']");
        if (btnUpload) btnUpload.click();
    };

    window.abrirDrawerAi = function() {
        switchTab("esteira_ia");
    };

    // Sincronizar sessão do usuário nos displays da sidebar
    window.addEventListener("DOMContentLoaded", function() {
        try {
            var raw = localStorage.getItem("cockpit_usuario_ativo");
            if (raw) {
                var u = JSON.parse(raw);
                var elNome = document.getElementById("sidebar-nome-usuario-display");
                if (elNome) elNome.innerText = u.nome;
                var elPerfil = document.getElementById("sidebar-perfil-usuario-display");
                if (elPerfil) elPerfil.innerText = u.cargo + " (" + u.nivel + ")";
            }
        } catch(e) {}
    });
})();
</script>
"""

content = re.sub(r'<script id="script-fase3-unificada">[\s\S]*?</script>', '', content)
if "</body>" in content:
    idx = content.rfind("</body>")
    content = content[:idx] + "\n" + js_fase3 + "\n" + content[idx:]
else:
    content = content + "\n" + js_fase3

tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(content)

shutil.move(tmp_path, painel_path)
print("✅ Fase 3 implantada com sucesso em painel.html!")
print("\n👉 Pressione Ctrl + F5 no navegador para ver o Cockpit com a Sidebar Unificada e os 4 Eixos!")
