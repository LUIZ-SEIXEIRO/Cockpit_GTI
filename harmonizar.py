import os
import re
import shutil

candidatos = [
    r"C:\Cockpit_GTI\frontend\painel.html",
    r"C:\Cockpit_GTI\painel.html"
]

arquivos_alvo = [p for p in candidatos if os.path.exists(p)]

if not arquivos_alvo:
    print("❌ Aviso: painel.html não foi localizado nos caminhos padrão.")
else:
    css_glassmorphism = """
<!-- ======================================================== -->
<!-- ESTILOS GLASSMORPHISM SAAS - HARMONIZAÇÃO KPI CARDS & PILLS -->
<!-- ======================================================== -->
<style id="glassmorphism-kpi-harmonization">
    /* 1. CARDS DE SCORECARD / KPI (Consolidado, Esteira, Rotina e Portfólio) */
    .kpi-row .kpi-card:not(.hero),
    .kpi-card:not(.hero) {
        background: rgba(255, 255, 255, 0.055) !important;
        backdrop-filter: blur(18px) -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        color: #ffffff !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
    }

    .kpi-row .kpi-card:not(.hero):hover,
    .kpi-card:not(.hero):hover {
        transform: translateY(-2px) !important;
        background: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 12px 36px 0 rgba(0, 0, 0, 0.45) !important;
    }

    /* Bordas temáticas e Glow dos semáforos nos cards */
    .kpi-card[style*="#ef4444"],
    .kpi-card[style*="rgb(239, 68, 68)"],
    .kpi-card[style*="border-left: 4px solid #ef4444"] {
        border-left: 4px solid #f87171 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 4px 0 14px -2px rgba(248, 113, 113, 0.35) !important;
    }
    .kpi-card[style*="#ea580c"],
    .kpi-card[style*="rgb(234, 88, 12)"],
    .kpi-card[style*="border-left: 4px solid #ea580c"] {
        border-left: 4px solid #fb923c !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 4px 0 14px -2px rgba(251, 146, 60, 0.35) !important;
    }
    .kpi-card[style*="#ca8a04"],
    .kpi-card[style*="rgb(202, 138, 4)"],
    .kpi-card[style*="border-left: 4px solid #ca8a04"] {
        border-left: 4px solid #facc15 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 4px 0 14px -2px rgba(250, 204, 21, 0.35) !important;
    }
    .kpi-card[style*="#16a34a"],
    .kpi-card[style*="rgb(22, 163, 74)"],
    .kpi-card[style*="border-left: 4px solid #16a34a"] {
        border-left: 4px solid #4ade80 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 4px 0 14px -2px rgba(74, 222, 128, 0.35) !important;
    }
    .kpi-card[style*="#0544cf"],
    .kpi-card[style*="border-left: 4px solid #0544cf"] {
        border-left: 4px solid #38bdf8 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 4px 0 14px -2px rgba(56, 189, 248, 0.35) !important;
    }

    /* Tipografia dos KPI Cards */
    .kpi-row .kpi-card:not(.hero) .kpi-title,
    .kpi-card:not(.hero) .kpi-title {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
    }

    /* Valores numéricos em cores vivas com glow difuso */
    #kpi-val-intervencao { color: #f87171 !important; text-shadow: 0 0 14px rgba(248, 113, 113, 0.45) !important; }
    #kpi-val-saneamento { color: #fb923c !important; text-shadow: 0 0 14px rgba(251, 146, 60, 0.45) !important; }
    #kpi-val-monitoramento { color: #facc15 !important; text-shadow: 0 0 14px rgba(250, 204, 21, 0.45) !important; }
    #kpi-val-fluxo-normal { color: #4ade80 !important; text-shadow: 0 0 14px rgba(74, 222, 128, 0.45) !important; }

    /* Subtítulos e legendas dos KPI cards */
    .kpi-row .kpi-card:not(.hero) span,
    .kpi-card:not(.hero) span {
        color: #94a3b8 !important;
    }

    /* Card Hero (Acervo Total) em vidro azul profundo */
    .kpi-card.hero {
        background: linear-gradient(135deg, rgba(0, 86, 210, 0.55) 0%, rgba(0, 45, 90, 0.8) 100%) !important;
        backdrop-filter: blur(18px) -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 45, 90, 0.45) !important;
        border-radius: 12px !important;
    }
    .kpi-card.hero .kpi-title { color: #93c5fd !important; }
    .kpi-card.hero .kpi-val { color: #ffffff !important; }

    /* 2. PÍLULAS DE NAVEGAÇÃO SUPERIORES */
    div:has(> .pill-filtro-dash),
    div:has(> .pill-filtro-farol) {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(16px) -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }

    .pill-filtro-dash.btn-primary,
    .pill-filtro-farol.btn-primary {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
        font-weight: 700 !important;
    }

    .pill-filtro-dash.btn-secondary,
    .pill-filtro-farol.btn-secondary {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) -webkit-backdrop-filter: blur(10px) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .pill-filtro-dash.btn-secondary:hover,
    .pill-filtro-farol.btn-secondary:hover {
        background: rgba(255, 255, 255, 0.14) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    /* 3. BARRA SUPERIOR E PÍLULAS DE USUÁRIO / DIRETORIA */
    .user-pill, #pill-diretoria-spaguas {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(14px) -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
        color: #e2e8f0 !important;
    }

    .user-pill select, #pill-diretoria-spaguas select {
        color: #f1f5f9 !important;
    }

    .user-pill select option, #pill-diretoria-spaguas select option {
        background: #0f172a !important;
        color: #f1f5f9 !important;
    }

    #btn-gestao-vista {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }

    #btn-gestao-vista:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        color: #ffffff !important;
    }
</style>
"""

    for target in arquivos_alvo:
        backup = target + ".bak_glass_cards"
        shutil.copy(target, backup)
        print(f"📦 Backup criado: {backup}")

        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        content = re.sub(r'<style id="glassmorphism-kpi-harmonization">[\s\S]*?</style>', '', content)

        if '</head>' in content:
            content = content.replace('</head>', css_glassmorphism + '\n</head>', 1)
        else:
            content = css_glassmorphism + '\n' + content

        content = content.replace(
            'style="display: flex; gap: 8px; margin-bottom: 20px; background: white;',
            'style="display: flex; gap: 8px; margin-bottom: 20px; background: rgba(255,255,255,0.04);'
        )
        content = content.replace(
            'style="display: flex; gap: 8px; margin-bottom: 16px; background: white;',
            'style="display: flex; gap: 8px; margin-bottom: 16px; background: rgba(255,255,255,0.04);'
        )

        tmp_target = target + ".tmp"
        with open(tmp_target, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)

        shutil.move(tmp_target, target)
        print(f"✅ Glassmorphism aplicado com sucesso em: {target}")

    print("\n🚀 Concluído! Pressione F5 no navegador para validar os cards integrados ao Dark Mode.")
