# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")

# 1. AJUSTAR CSS DA TOPBAR NO painel.html
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    antigo_css = """.topbar-title h2 {
            font-size: 16px;
            font-weight: 700;
            color: var(--sp-text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .topbar-title span {
            font-size: 12px;
            color: var(--sp-text-muted);
            font-weight: 400;
        }"""

    novo_css = """.topbar-title {
            min-width: 260px;
            max-width: 380px;
            flex-shrink: 1;
            overflow: hidden;
        }

        .topbar-title h2 {
            font-size: 14px;
            font-weight: 700;
            color: var(--sp-text-main);
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0 0 2px 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .topbar-title span {
            font-size: 11px;
            color: var(--sp-text-muted);
            font-weight: 400;
            white-space: nowrap;
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
        }"""

    if antigo_css in html:
        html = html.replace(antigo_css, novo_css)
        with open(caminho_painel, "w", encoding="utf-8") as f:
            f.write(html)
        print("1. CSS da TopBar ajustado no painel.html!")
    else:
        print("1. CSS da TopBar ja estava ajustado.")

# 2. AJUSTAR LEDS COM UNICODE ESCAPE DIRETO NO conector_api.js
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    # Substitui a entidade literal pelo escape unicode nativo JS (\u{1F7E2} e \u{1F534})
    js = js.replace("'&#128994;'", "'\\u{1F7E2}'")
    js = js.replace("'&#128308;'", "'\\u{1F534}'")
    js = js.replace("&#128994;", "\\u{1F7E2}")
    js = js.replace("&#128308;", "\\u{1F534}")

    with open(caminho_js, "w", encoding="utf-8") as f:
        f.write(js)
    print("2. LEDs da TopBar atualizados com icones visuais nativos no conector_api.js!")

print("Acabamento da TopBar aplicado com sucesso!")
