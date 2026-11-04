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

glass_css_and_js = """
<!-- =========================================================================
     DESIGN SYSTEM v11.0: GLASSMORPHISM SAAS DUAL-THEME (DARK DEFAULT & LIGHT)
     ========================================================================= -->
<style id="cockpit-glassmorphism-v11">
:root, [data-theme="dark"] {
    --bg-canvas: #090d16;
    --bg-sidebar: rgba(13, 19, 33, 0.78);
    --bg-header: rgba(13, 19, 33, 0.72);
    --bg-glass-card: rgba(255, 255, 255, 0.055);
    --bg-glass-elevated: rgba(255, 255, 255, 0.085);
    --bg-glass-input: rgba(15, 23, 42, 0.65);
    --border-glass: rgba(255, 255, 255, 0.12);
    --border-glass-highlight: rgba(56, 189, 248, 0.35);
    --shadow-glass: 0 14px 34px -6px rgba(0, 0, 0, 0.55), inset 0 1px 0 0 rgba(255, 255, 255, 0.12);
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-tech: #00e5ff;
    --accent-primary: #3b82f6;
    --accent-ai: #8b5cf6;
    --table-row-hover: rgba(59, 130, 246, 0.12);
    --table-stripe: rgba(255, 255, 255, 0.02);
    --glow-1: rgba(5, 68, 207, 0.28);
    --glow-2: rgba(139, 92, 246, 0.22);
    --glow-3: rgba(6, 182, 212, 0.18);
}

[data-theme="light"] {
    --bg-canvas: #f2f6fc;
    --bg-sidebar: rgba(255, 255, 255, 0.78);
    --bg-header: rgba(255, 255, 255, 0.75);
    --bg-glass-card: rgba(255, 255, 255, 0.68);
    --bg-glass-elevated: rgba(255, 255, 255, 0.92);
    --bg-glass-input: rgba(255, 255, 255, 0.90);
    --border-glass: rgba(15, 23, 42, 0.09);
    --border-glass-highlight: rgba(2, 132, 199, 0.35);
    --shadow-glass: 0 10px 28px -6px rgba(15, 45, 89, 0.08), inset 0 1px 0 0 rgba(255, 255, 255, 0.85);
    --text-primary: #1a1a1a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --accent-tech: #0284c7;
    --accent-primary: #2563eb;
    --accent-ai: #7c3aed;
    --table-row-hover: rgba(2, 132, 199, 0.08);
    --table-stripe: rgba(15, 23, 42, 0.02);
    --glow-1: rgba(59, 130, 246, 0.14);
    --glow-2: rgba(139, 92, 246, 0.11);
    --glow-3: rgba(6, 182, 212, 0.10);
}

/* Base & Aurora Backdrop Glow */
body {
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
    transition: background-color 0.35s ease, color 0.35s ease;
    position: relative;
    overflow-x: hidden;
}

#aurora-backdrop-container {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.aurora-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(110px);
    transition: background 0.5s ease;
}

.aurora-orb-1 {
    width: 620px;
    height: 620px;
    top: -180px;
    left: -120px;
    background: radial-gradient(circle, var(--glow-1) 0%, transparent 70%);
}

.aurora-orb-2 {
    width: 540px;
    height: 540px;
    top: 22%;
    right: -140px;
    background: radial-gradient(circle, var(--glow-2) 0%, transparent 70%);
}

.aurora-orb-3 {
    width: 580px;
    height: 580px;
    bottom: -200px;
    left: 28%;
    background: radial-gradient(circle, var(--glow-3) 0%, transparent 70%);
}

/* Estrutura Principal sobre o Backdrop */
#sidebar, .main-wrapper, header, .content-scroll {
    position: relative;
    z-index: 1;
}

.main-wrapper, .content-scroll {
    background: transparent !important;
}

/* Sidebar Glassmorphism */
#sidebar {
    background: var(--bg-sidebar) !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    border-right: 1px solid var(--border-glass) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25) !important;
}

[data-theme="light"] #sidebar .brand-title,
[data-theme="light"] #sidebar .nav-item {
    color: #1e293b !important;
}

[data-theme="light"] #sidebar .nav-section-title {
    color: #0284c7 !important;
}

#sidebar .nav-item {
    border-radius: 10px !important;
    margin: 3px 10px !important;
    padding: 9px 12px !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
}

#sidebar .nav-item:hover {
    background: var(--bg-glass-elevated) !important;
    border-color: var(--border-glass) !important;
    transform: translateX(2px);
}

#sidebar .nav-item.active {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.28) 0%, rgba(139, 92, 246, 0.22) 100%) !important;
    border: 1px solid var(--border-glass-highlight) !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    color: var(--text-primary) !important;
}

/* Header Superior Glassmorphism */
header, .top-header {
    background: var(--bg-header) !important;
    backdrop-filter: blur(18px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
    border-bottom: 1px solid var(--border-glass) !important;
    color: var(--text-primary) !important;
}

header h2, #page-title {
    color: var(--text-primary) !important;
}

/* Cards de Vidro Fosco (KPIs, Tabelas, Gráficos) */
.kpi-card, .table-card, .chart-card {
    background: var(--bg-glass-card) !important;
    backdrop-filter: blur(18px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow-glass) !important;
    color: var(--text-primary) !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-glass-highlight) !important;
}

.kpi-title, .chart-header, .table-header-title {
    color: var(--text-secondary) !important;
}

.kpi-val {
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

.table-header-bar, .pagination-bar {
    background: var(--bg-glass-elevated) !important;
    border-bottom: 1px solid var(--border-glass) !important;
    color: var(--text-primary) !important;
}

/* Banners Superiores com Brilho Translúcido */
.page-banner {
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.35) !important;
    backdrop-filter: blur(14px) !important;
}

/* Tabelas & Tipografia Adaptativa */
table {
    color: var(--text-primary) !important;
}

thead th {
    background: rgba(15, 23, 42, 0.75) !important;
    color: #f8fafc !important;
    border-bottom: 1px solid var(--border-glass) !important;
    font-weight: 700 !important;
}

[data-theme="light"] thead th {
    background: rgba(15, 45, 89, 0.92) !important;
    color: #ffffff !important;
}

tbody tr {
    border-bottom: 1px solid var(--border-glass) !important;
    transition: background-color 0.15s ease !important;
}

tbody tr:nth-child(even) {
    background-color: var(--table-stripe) !important;
}

tbody tr:hover {
    background-color: var(--table-row-hover) !important;
}

tbody td {
    color: var(--text-primary) !important;
}

/* Inputs, Selects e Textareas em Vidro */
input[type="text"], input[type="number"], input[type="password"], select, textarea {
    background: var(--bg-glass-input) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(8px) !important;
}

input::placeholder, textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Botões e Ações (CTAs Vibrantes) */
.btn-primary {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35) !important;
    border-radius: 8px !important;
}

.btn-secondary {
    background: var(--bg-glass-elevated) !important;
    border: 1px solid var(--border-glass) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

.btn-secondary:hover {
    border-color: var(--border-glass-highlight) !important;
}

/* Override suave para divs com background branco chumbado no modo escuro */
[data-theme="dark"] .table-card div[style*="background: #ffffff"],
[data-theme="dark"] .table-card div[style*="background:#ffffff"],
[data-theme="dark"] .table-card div[style*="background: white"],
[data-theme="dark"] .table-card div[style*="background: #f8fafc"],
[data-theme="dark"] .table-card div[style*="background:#f8fafc"],
[data-theme="dark"] .chart-card div[style*="background: #ffffff"],
[data-theme="dark"] .chart-card div[style*="background: #f8fafc"] {
    background: rgba(15, 23, 42, 0.45) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-glass) !important;
}

[data-theme="dark"] strong,
[data-theme="dark"] h3,
[data-theme="dark"] h4 {
    color: var(--text-primary) !important;
}

/* Botão Comutador Dark / Light no Topo */
#btn-theme-toggle-v11 {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 800;
    cursor: pointer;
    border: 1px solid var(--border-glass-highlight);
    background: var(--bg-glass-elevated);
    color: var(--text-primary);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
}
#btn-theme-toggle-v11:hover {
    transform: scale(1.03);
}
</style>

<script>
(function inicializarGlassmorphismV11() {
    // 1. Aplica tema salvo ou Dark Mode como Default conforme especificação
    var temaSalvo = localStorage.getItem('sagti_theme_v11') || 'dark';
    document.documentElement.setAttribute('data-theme', temaSalvo);

    window.alternarTemaCockpitV11 = function() {
        var atual = document.documentElement.getAttribute('data-theme') || 'dark';
        var novo = (atual === 'dark') ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', novo);
        localStorage.setItem('sagti_theme_v11', novo);
        atualizarTextoBotaoTema(novo);
    };

    function atualizarTextoBotaoTema(tema) {
        var btn = document.getElementById('btn-theme-toggle-v11');
        if (!btn) return;
        if (tema === 'dark') {
            btn.innerHTML = '☀️ Modo Claro (Light)';
            btn.title = 'Mudar para interface clara (Light Glass)';
        } else {
            btn.innerHTML = '🌙 Modo Escuro (Dark)';
            btn.title = 'Mudar para interface escura (Dark Glass Default)';
        }
    }

    function montarEstruturaVisual() {
        // 2. Injeta as esferas de luz Aurora Backdrop se ainda não existirem
        if (!document.getElementById('aurora-backdrop-container')) {
            var aurora = document.createElement('div');
            aurora.id = 'aurora-backdrop-container';
            aurora.innerHTML = '<div class="aurora-orb aurora-orb-1"></div>' +
                               '<div class="aurora-orb aurora-orb-2"></div>' +
                               '<div class="aurora-orb aurora-orb-3"></div>';
            document.body.insertBefore(aurora, document.body.firstChild);
        }

        // 3. Insere o botão de alternância Dark/Light no cabeçalho superior
        if (!document.getElementById('btn-theme-toggle-v11')) {
            var header = document.querySelector('header');
            if (header) {
                var btn = document.createElement('button');
                btn.id = 'btn-theme-toggle-v11';
                btn.type = 'button';
                btn.onclick = window.alternarTemaCockpitV11;
                var rightBox = header.lastElementChild || header;
                rightBox.insertBefore(btn, rightBox.firstChild);
                atualizarTextoBotaoTema(document.documentElement.getAttribute('data-theme') || 'dark');
            }
        }

        // 4. Reorganiza os títulos de seção da Sidebar nas 3 Linhas Primárias Estratégicas
        var secTitles = document.querySelectorAll('#sidebar .nav-section-title');
        if (secTitles.length >= 3) {
            if (secTitles[0]) secTitles[0].innerHTML = '📊 EIXO 1: DASHBOARD & DECISÃO 360°';
            if (secTitles[1]) secTitles[1].innerHTML = '🏛️ EIXO 2: COCKPIT ADM, SEI & IA';
            if (secTitles[2]) secTitles[2].innerHTML = '🤝 EIXO 3: REUNIÕES & DIRETORIA';
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', montarEstruturaVisual);
    } else {
        montarEstruturaVisual();
    }
})();
</script>
"""

for painel_path in alvos:
    print(f"Aplicando Glassmorphism v11.0 em: {painel_path}")
    shutil.copyfile(painel_path, painel_path + ".bak")

    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Remove versão anterior do bloco se já tiver sido aplicada
    html = re.sub(r'<!-- =========================================================================\s*DESIGN SYSTEM v11\.0:.*?</script>', '', html, flags=re.DOTALL)

    pos_body = html.rfind("</body>")
    if pos_body != -1:
        html = html[:pos_body] + "\n" + glass_css_and_js + "\n" + html[pos_body:]
    else:
        html += "\n" + glass_css_and_js

    tmp = painel_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp, painel_path)
    print(f"  -> {painel_path} atualizado com sucesso!")

print("\n=== DESIGN GLASSMORPHISM DUAL-THEME APLICADO! ===")
