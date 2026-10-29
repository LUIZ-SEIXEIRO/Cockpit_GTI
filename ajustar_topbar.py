# -*- coding: utf-8 -*-
import os

caminho_js = os.path.join(os.getcwd(), "frontend", "conector_api.js")
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8") as f:
        codigo = f.read()

    # Ajusta o ponto de ancoragem no DOM para o container de acoes da Topbar
    codigo_corrigido = codigo.replace(
        "topbar.insertBefore(containerInfra, elRef);",
        "elRef.parentNode.insertBefore(containerInfra, elRef);"
    )

    with open(caminho_js, "w", encoding="utf-8") as f:
        f.write(codigo_corrigido)

    print("Widget de telemetria acoplado na TopBar com sucesso!")
