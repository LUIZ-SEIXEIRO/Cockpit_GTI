# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")

# 1. INJETAR REGRAS DE ROLAGEM GLOBAL NO painel.html
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    css_rolagem = '''
        /* --- ROLAGEM GLOBAL FLUIDA DO CONTEÚDO PRINCIPAL --- */
        #main {
            flex: 1 !important;
            height: 100vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            display: flex !important;
            flex-direction: column !important;
        }

        #topbar {
            position: sticky !important;
            top: 0 !important;
            z-index: 100 !important;
            flex-shrink: 0 !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }

        .tab-view {
            padding: 24px;
        }

        .tab-view.active {
            display: block !important;
            min-height: calc(100vh - 120px);
            padding-bottom: 90px !important;
        }

        /* Barra de rolagem estilizada e visível */
        #main::-webkit-scrollbar {
            width: 9px !important;
        }
        #main::-webkit-scrollbar-track {
            background: #f1f5f9 !important;
        }
        #main::-webkit-scrollbar-thumb {
            background: #94a3b8 !important;
            border-radius: 6px !important;
            border: 2px solid #f1f5f9 !important;
        }
        #main::-webkit-scrollbar-thumb:hover {
            background: #64748b !important;
        }
    '''

    if "/* --- ROLAGEM GLOBAL FLUIDA" not in html:
        idx_style = html.find("</style>")
        if idx_style != -1:
            html = html[:idx_style] + css_rolagem + "\n    " + html[idx_style:]
            with open(caminho_painel, "w", encoding="utf-8") as f:
                f.write(html)
            print("1. Regras de rolagem global injetadas com sucesso no painel.html!")
    else:
        print("1. Regras de rolagem já existiam no painel.html.")

# 2. ATUALIZAR conector_api.js PARA ROLAR O #main AO TROCAR DE ABA
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    # Atualiza o reset de scroll para mirar no #main
    js = js.replace(
        "var cs = document.querySelector('.content-scroll') || document.querySelector('#main');\n        if (cs && cs.scrollTop) {\n            cs.scrollTop = 0;\n        }",
        "var mainEl = document.getElementById('main') || document.querySelector('.content-scroll');\n        if (mainEl) mainEl.scrollTop = 0;"
    )

    with open(caminho_js, "w", encoding="utf-8") as f:
        f.write(js)
    print("2. conector_api.js atualizado para controlar a rolagem do #main!")

print("Rolagem ativada com sucesso em todas as abas!")
