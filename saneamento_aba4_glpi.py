# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")

if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Adicionar botao direto para atendimento.spaguas.sp.gov.br no banner do GLPI
    antigo_badge_glpi = '''<span id="glpi-status-badge" style="background:rgba(16,185,129,0.22); border:1px solid rgba(16,185,129,0.5); color:#ecfdf5; padding:5px 12px; border-radius:20px; font-size:11.5px; font-weight:700;">
                        &#128994; GLPI 10 REST API Conectada (:8088 / :8096)
                    </span>'''

    novo_badge_glpi = '''<a href="https://atendimento.spaguas.sp.gov.br" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="font-size:11px; padding:5px 10px; background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); color:#fff; text-decoration:none; font-weight:700;">🌐 Abrir atendimento.spaguas.sp.gov.br ↗</a>
                    <span id="glpi-status-badge" style="background:rgba(16,185,129,0.22); border:1px solid rgba(16,185,129,0.5); color:#ecfdf5; padding:5px 12px; border-radius:20px; font-size:11.5px; font-weight:700;">
                        &#128994; GLPI 10 Produção (Read-Only Ativo)
                    </span>'''

    # 2. Tornar o numero do chamado (#9209 etc) um link direto para o chamado no GLPI
    antigo_td_ticket = '\'<td style="padding:9px 12px;font-weight:800;color:#0056d2;font-family:monospace;"><a href="javascript:void(0)" onclick="window.navegarDrillDown360(\\\'glpi\\\', \\\'#\' + t.id + \'\\\')" class="link-drilldown-v9">#\' + t.id + \'</a></td>\''

    novo_td_ticket = '\'<td style="padding:9px 12px;font-weight:800;font-family:monospace;"><a href="https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=\' + t.id + \'" target="_blank" rel="noopener noreferrer" style="color:#0056d2;text-decoration:underline;" title="Abrir Chamado no GLPI Oficial">#\' + t.id + \'</a></td>\''

    alterado = False
    if antigo_badge_glpi in html:
        html = html.replace(antigo_badge_glpi, novo_badge_glpi)
        alterado = True

    if antigo_td_ticket in html:
        html = html.replace(antigo_td_ticket, novo_td_ticket)
        alterado = True

    if alterado:
        with open(caminho_painel, "w", encoding="utf-8") as f:
            f.write(html)
        print("Aba 4 (Gestão GLPI & ITSM) saneada com sucesso!")
    else:
        print("Aba 4 já possuía os ajustes do GLPI de produção.")
