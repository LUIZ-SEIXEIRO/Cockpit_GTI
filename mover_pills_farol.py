# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" REORGANIZAÇÃO VISUAL: MOVER FILTRO DE FARÓIS PARA ACIMA DA TABELA")
print(" Tela: Visão Estratégica & Faróis de Criticidade")
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

    # Localizar o bloco de pills no topo
    pattern_pills = r'(\s*<!-- SELETOR DE MODOS DE VISUALIZAÇÃO \(PILLS\) -->\s*<div[^>]*>[\s\S]*?</div>)'
    m_pills = re.search(pattern_pills, html)

    target_str = '<!-- TABELA DINÂMICA COM FILTRO DE FAROL E CUSTÓDIA -->'
    idx_target = html.find(target_str)

    if m_pills and idx_target != -1:
        if m_pills.start() < idx_target:
            pills_html = m_pills.group(1)
            
            # Ajustar para o acabamento dark glassmorphism
            pills_styled = pills_html.replace('background: white;', 'background: rgba(15, 23, 42, 0.6);')
            pills_styled = pills_styled.replace('border: 1px solid var(--sp-border);', 'border: 1px solid rgba(255, 255, 255, 0.08);')
            pills_styled = pills_styled.replace('border-radius: 8px;', 'border-radius: 12px;')

            # Remover do topo
            html_sem_pills = html[:m_pills.start()] + html[m_pills.end():]
            
            # Inserir imediatamente antes da tabela de processos filtrados
            idx_novo_target = html_sem_pills.find(target_str)
            html_final = html_sem_pills[:idx_novo_target] + pills_styled + '\n\n            ' + html_sem_pills[idx_novo_target:]

            # Validar integridade do DOM
            open_divs = len(re.findall(r'<div\b', html_final, re.IGNORECASE))
            close_divs = len(re.findall(r'</div\b', html_final, re.IGNORECASE))
            diff = open_divs - close_divs

            if diff == 0:
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(html_final)
                print(f"[*] {caminho}: Filtro movido para cima da tabela com sucesso! (Div balance = 0)")
            else:
                print(f"[!] Erro de balanceamento de divs (diff={diff}). Alteração cancelada.")
        else:
            print(f"[*] {caminho}: O filtro já está posicionado acima da tabela!")
    else:
        print(f"[!] Marcadores HTML não localizados em {caminho}.")

print("\n" + "=" * 70)
print(" REORGANIZAÇÃO CONCLUÍDA")
print("=" * 70)
