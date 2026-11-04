# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" CORREÇÃO DE GLYPH / TYPO: CARD 'EM ESPERA / AGENDADOS'")
print(" Tela: Portfólio OpenProject (500 Work Packages)")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Substitui a entidade truncada/glitch por emoji limpo e texto correto
    pattern = r'<div class="kpi-title">.*?ESPERA / AGENDADOS</div>'
    novo_titulo = '<div class="kpi-title">⏳ EM ESPERA / AGENDADOS</div>'
    
    html_mod = re.sub(pattern, novo_titulo, html, count=1)

    open_divs = len(re.findall(r'<div\b', html_mod, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html_mod, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0 and html != html_mod:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html_mod)
        print(f"[*] {caminho}: Título corrigido para '⏳ EM ESPERA / AGENDADOS'! (Div balance = 0)")
    elif html == html_mod:
        print(f"[*] {caminho}: O título já está com a grafia correta.")
    else:
        print(f"[!] Erro de balanceamento em {caminho}.")

print("\n" + "=" * 70)
print(" CORREÇÃO CONCLUÍDA")
print("=" * 70)
