import os
import shutil

print("[1/3] Identificando arquivo mestre do frontend...")
painel_path = os.path.join("frontend", "painel.html")
if not os.path.exists(painel_path):
    painel_path = "painel.html"

shutil.copyfile(painel_path, painel_path + ".bak")

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

print("[2/3] Aplicando ajustes no layout do Chat e na exibicao do Pool de IAs...")

# 1. Ajuste da altura do grid do chat para fixar a barra de input na base visivel da tela
old_grid = 'style="display: grid; grid-template-columns: 1fr; gap: 16px; height: calc(100vh - 195px); min-height: 580px;"'
new_grid = 'style="display: grid; grid-template-columns: 1fr; gap: 16px; height: calc(100vh - 250px); min-height: 480px; max-height: calc(100vh - 250px);"'

if old_grid in html:
    html = html.replace(old_grid, new_grid)
    print("  -> Altura do Chat IA ajustada: campo de digitacao agora fica 100% visivel no rodape!")

# 2. Ajuste fino na sub-aba do Pool de IAs para garantir visibilidade plena
# Substitui a chamada da sub-aba no alternarSubConfig com bloco seguro
old_fn_chunk = "const target = document.getElementById('subview-cfg-' + modo);\n        if (target) target.style.display = 'block';"
new_fn_chunk = """const target = document.getElementById('subview-cfg-' + modo);
        if (target) {
            target.style.display = 'block';
            target.style.visibility = 'visible';
            target.style.opacity = '1';
        }"""

if old_fn_chunk in html:
    html = html.replace(old_fn_chunk, new_fn_chunk)
    print("  -> Visibilidade do container do Pool das 3 IAs forcada com sucesso!")

# 3. Garante que subview-cfg-agentes seja renderizado sem bloqueios de estilo inline
html = html.replace('<div id="subview-cfg-agentes" class="subview-cfg" style="display: none;">', '<div id="subview-cfg-agentes" class="subview-cfg">')

# 4. Gravação atômica segura
tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)
shutil.move(tmp_path, painel_path)

print("[3/3] Ajustes concluidos com sucesso!")
