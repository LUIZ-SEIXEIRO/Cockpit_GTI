import os
import re
import shutil

alvos = []
for p in [os.path.join("frontend", "painel.html"), "painel.html"]:
    if os.path.exists(p):
        alvos.append(p)

if not alvos:
    print("Erro: Nenhum painel.html encontrado!")
    exit(1)

css_harmonizacao = """
<style id="cockpit-glass-harmony-v11">
/* =========================================================================
   HARMONIZAÇÃO GLASSMORPHISM: CARDS TRANSLÚCIDOS & CONTRASTE WCAG AAA
   ========================================================================= */

/* Transforma todos os cards brancos sólidos em vidro fosco no Dark Mode */
[data-theme="dark"] .kpi-card,
[data-theme="dark"] .table-card,
[data-theme="dark"] .chart-card,
[data-theme="dark"] div[style*="background: white"],
[data-theme="dark"] div[style*="background: #ffffff"],
[data-theme="dark"] div[style*="background:#ffffff"],
[data-theme="dark"] div[style*="background: #f8fafc"],
[data-theme="dark"] div[style*="background:#f8fafc"] {
    background: rgba(255, 255, 255, 0.055) !important;
    backdrop-filter: blur(18px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 10px 30px -4px rgba(0, 0, 0, 0.5) !important;
    color: #ffffff !important;
}

/* Card Hero no Dark Mode */
[data-theme="dark"] .kpi-card.hero {
    background: linear-gradient(135deg, rgba(5, 68, 207, 0.45) 0%, rgba(2, 45, 90, 0.6) 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.35) !important;
}

/* Tipografia e Contraste dos Valores Numéricos */
[data-theme="dark"] .kpi-val,
[data-theme="dark"] span[id^="kpi-val-"] {
    color: #ffffff !important;
    font-weight: 800 !important;
}

[data-theme="dark"] #kpi-val-rotina { color: #38bdf8 !important; }
[data-theme="dark"] #kpi-val-esteira { color: #60a5fa !important; }
[data-theme="dark"] #kpi-val-portfolio { color: #c084fc !important; }

/* Subtítulos e Rótulos Secundários */
[data-theme="dark"] .kpi-title,
[data-theme="dark"] span[id^="kpi-sub-"],
[data-theme="dark"] div[style*="color: #64748b"],
[data-theme="dark"] span[style*="color: #64748b"],
[data-theme="dark"] div[style*="color: #475569"],
[data-theme="dark"] span[style*="color: #475569"],
[data-theme="dark"] div[style*="color: #334155"] {
    color: #94a3b8 !important;
}

/* Pílulas de Modo do Dashboard (Acima dos Cards) */
.pill-filtro-dash {
    border-radius: 20px !important;
    padding: 7px 16px !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

[data-theme="dark"] .pill-filtro-dash.btn-secondary {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    backdrop-filter: blur(14px) !important;
}

[data-theme="dark"] .pill-filtro-dash.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.16) !important;
    color: #ffffff !important;
    border-color: rgba(56, 189, 248, 0.5) !important;
    transform: translateY(-1px);
}

[data-theme="dark"] .pill-filtro-dash.btn-primary {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.45) !important;
}

/* Categorias da Sidebar */
.menu-category {
    font-size: 10.5px !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    padding: 14px 14px 6px 14px !important;
    color: #38bdf8 !important;
}

[data-theme="light"] .menu-category {
    color: #0369a1 !important;
}
</style>

<script>
// Reorganização dinâmica da Sidebar nos 3 Eixos Estratégicos
(function reorganizarSidebar3Eixos() {
    function aplicarMenu3Eixos() {
        var menu = document.querySelector('#sidebar .sidebar-menu');
        if (!menu) return;

        // Se já foi reorganizado, não repete
        if (menu.getAttribute('data-reorganizado-v11') === '1') return;
        menu.setAttribute('data-reorganizado-v11', '1');

        menu.innerHTML = `
            <!-- EIXO 1: DASHBOARD & DECISÃO 360° -->
            <div class="menu-category">📊 EIXO 1: DASHBOARD & DECISÃO 360°</div>
            <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')">
                <div class="nav-item-left">🌐 <span>Central de Dashboards</span></div>
                <span class="nav-badge">360°</span>
            </div>
            <div class="nav-item" data-tab="visao_estrategica" onclick="switchTab('visao_estrategica')">
                <div class="nav-item-left">🎯 <span>Faróis & Gargalos (87)</span></div>
                <span class="nav-badge" style="background:#f59e0b; color:#fff;">87</span>
            </div>
            <div class="nav-item" data-tab="portfolio_openproject" onclick="switchTab('portfolio_openproject')">
                <div class="nav-item-left">🏗️ <span>Portfólio OpenProject</span></div>
                <span class="nav-badge" style="background:#10b981; color:#fff;">500</span>
            </div>
            <div class="nav-item" data-tab="tracks_sagti" onclick="switchTab('tracks_sagti')">
                <div class="nav-item-left">⚡ <span>Tracks SA-GTI (A-018)</span></div>
                <span class="nav-badge" style="background:#0544cf; color:#fff;">97</span>
            </div>
            <div class="nav-item" data-tab="pdtic_eixos" onclick="switchTab('pdtic_eixos')">
                <div class="nav-item-left">🧭 <span>Governança PDTIC & KPIs</span></div>
                <span class="nav-badge" style="background:#7c3aed; color:#fff;">35</span>
            </div>
            <div class="nav-item" data-tab="gestao_glpi" onclick="switchTab('gestao_glpi')">
                <div class="nav-item-left">🎫 <span>Atendimento GLPI 10</span></div>
                <span class="nav-badge" style="background:#0284c7; color:#fff;">13</span>
            </div>

            <!-- EIXO 2: COCKPIT ADM, SEI & IA -->
            <div class="menu-category">🏛️ EIXO 2: COCKPIT ADM, SEI & IA</div>
            <div class="nav-item" data-tab="consulta" onclick="switchTab('consulta')">
                <div class="nav-item-left">📂 <span>Acervo SEI (Upload PDF v7.1)</span></div>
                <span class="nav-badge" style="background:#0284c7; color:#fff;">197</span>
            </div>
            <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')">
                <div class="nav-item-left">🖥️ <span>Mesa de Trabalho (Custódia)</span></div>
                <span class="nav-badge" style="background:#10b981; color:#fff;">Luiz</span>
            </div>
            <div class="nav-item" data-tab="esteira_ia" onclick="switchTab('esteira_ia')">
                <div class="nav-item-left">🤖 <span>Assistente Pessoal IA & RACI</span></div>
                <span class="nav-badge" style="background:#8b5cf6; color:#fff;">Pool</span>
            </div>
            <div class="nav-item" data-tab="cadernos" onclick="switchTab('cadernos')">
                <div class="nav-item-left">📚 <span>Cadernos, Toolkits & A4</span></div>
                <span class="nav-badge">15</span>
            </div>

            <!-- EIXO 3: REUNIÕES & PRESTAÇÃO DE CONTAS -->
            <div class="menu-category">🤝 EIXO 3: REUNIÕES & PRESTAÇÃO DE CONTAS</div>
            <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')">
                <div class="nav-item-left">⏱️ <span>War Room (Ata A4 & Pauta)</span></div>
                <span class="nav-badge" style="background:#0544cf; color:#fff;">15m</span>
            </div>
            <div class="nav-item" data-tab="gestao_agil" onclick="switchTab('gestao_agil')">
                <div class="nav-item-left">📋 <span>Sprint Planning & Kanban</span></div>
                <span class="nav-badge">Agile</span>
            </div>
            <div class="nav-item" data-tab="auditoria" onclick="switchTab('auditoria')">
                <div class="nav-item-left">🛡️ <span>Auditoria TCE-SP & Súmula 269</span></div>
                <span class="nav-badge" style="background:#10b981; color:#fff;">88.5%</span>
            </div>

            <!-- GAVETA DE INFRAESTRUTURA & CONFIGURAÇÕES -->
            <div class="menu-category" style="color: #64748b;">⚙️ SISTEMA</div>
            <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')">
                <div class="nav-item-left">🔧 <span>Configurações & RBAC</span></div>
                <span class="nav-badge">Admin</span>
            </div>
        `;

        // Mantém a aba ativa selecionada visualmente
        var tabAtual = window.currentTab || 'dashboards';
        var itemAtivo = menu.querySelector(`.nav-item[data-tab="${tabAtual}"]`);
        if (itemAtivo) {
            menu.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            itemAtivo.classList.add('active');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', aplicarMenu3Eixos);
    } else {
        aplicarMenu3Eixos();
    }
})();
</script>
"""

for painel_path in alvos:
    print(f"Harmonizando Glassmorphism e Sidebar em: {painel_path}")
    shutil.copyfile(painel_path, painel_path + ".bak")

    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Remove regras anteriores se existirem
    html = re.sub(r'<style id="cockpit-glass-harmony-v11">.*?</script>', '', html, flags=re.DOTALL)

    pos_body = html.rfind("</body>")
    if pos_body != -1:
        html = html[:pos_body] + "\n" + css_harmonizacao + "\n" + html[pos_body:]
    else:
        html += "\n" + css_harmonizacao

    tmp = painel_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp, painel_path)
    print(f"  -> {painel_path} atualizado com sucesso!")

print("\n=== HARMONIZAÇÃO GLASSMORPHISM E SIDEBAR CONCLUÍDA! ===")
