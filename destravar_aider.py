# -*- coding: utf-8 -*-
import os, glob

# 1. LIMPAR HISTÓRICO CORROMPIDO DO AIDER (.aider*)
arquivos_aider = glob.glob(".aider*")
for arq in arquivos_aider:
    try:
        if os.path.isfile(arq): os.remove(arq)
    except: pass
print("1. Arquivos de cache e histórico do Aider (.aider*) limpos.")

# 2. SANITIZAR conector_api.js (CONVERTER EMOJIS EM ENTIDADES HTML PURAS)
caminho_js = os.path.join(os.getcwd(), "frontend", "conector_api.js")
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        codigo = f.read()

    # Mapeamento para entidades numéricas HTML (blindagem contra surrogates no Windows)
    mapa_emojis = {
        '📊': '&#128202;', '🎯': '&#127919;', '🏗️': '&#127959;&#65039;', '🏗': '&#127959;',
        '⚡': '&#9889;', '🧭': '&#129517;', '🎫': '&#127915;', '📁': '&#128194;',
        '🖥️': '&#128421;&#65039;', '🖥': '&#128421;', '📋': '&#128203;',
        '⏱️': '&#9201;&#65039;', '⏱': '&#9201;', '🤖': '&#129302;',
        '🛡️': '&#128737;&#65039;', '🛡': '&#128737;', '📚': '&#128218;',
        '🔧': '&#128295;', '⭐': '&#11088;', '🟢': '&#128994;', '🔴': '&#128308;',
        '🔄': '&#128260;', '📡': '&#128225;'
    }
    for emoji, entidade in mapa_emojis.items():
        codigo = codigo.replace(emoji, entidade)

    # Remove qualquer byte surrogate remanescente
    codigo_limpo = codigo.encode("utf-8", "surrogateescape").decode("utf-8", "ignore")

    with open(caminho_js, "w", encoding="utf-8") as f:
        f.write(codigo_limpo)
    print("2. conector_api.js sanitizado com entidades HTML (zero surrogates).")

print("Ambiente destravado com sucesso!")
