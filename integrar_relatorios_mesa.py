# -*- coding: utf-8 -*-
import os, sys

caminhos = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]
alvos = [p for p in caminhos if os.path.exists(p)]

pill = (
    '                            <button type="button" class="btn btn-secondary pill-filtro-mesa" id="btn-mesa-relatorios" onclick="window.alternarModoMesa(\'relatorios\')" style="padding: 5px 12px; font-size: 11.5px; border-radius: 6px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; font-weight: 700;">\n'
    '                                📑 Relatórios Daily &amp; Sprints (<span id="count-mesa-relatorios">4</span>)\n'
    '                            </button>\n'
)

for a in alvos:
    with open(a, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()
    if 'id="btn-mesa-relatorios"' not in c and 'id="btn-mesa-openproject"' in c:
        c = c.replace('id="btn-mesa-openproject"', 'id="btn-mesa-openproject"')
        c = c.replace('</button>\n                        </div>', '</button>\n' + pill + '                        </div>', 1)
    with open(a, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"[OK] Atualizado: {a}")
print("[SUCESSO] Relatórios integrados à Mesa de Trabalho!")
