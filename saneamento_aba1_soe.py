# -*- coding: utf-8 -*-
import os

caminho_painel = os.path.join(os.getcwd(), "frontend", "painel.html")
if not os.path.exists(caminho_painel):
    print("ERRO: painel.html não encontrado em", caminho_painel)
    exit(1)

with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Substituições cirúrgicas para desacoplar a planilha legada e apontar para o SOE
substituicoes = [
    ("Acompanhamento de Processos — SA-GTI | Base Atualizada: 22/09/2026",
     "Gestão de Processos & Contratos — SA-GTI | Base Integrada: SOE / Outorgas & SEI-SP"),
    ("Acompanhamento de Processos - SA-GTI | Base Atualizada: 22/09/2026",
     "Gestão de Processos & Contratos — SA-GTI | Base Integrada: SOE / Outorgas & SEI-SP"),
    ("Base Atualizada: 22/09/2026",
     "Base Integrada: SOE / Outorgas & SEI-SP"),
    ("Visão executiva integrada de todos os 179 processos de TIC da SA-GTI",
     "Visão executiva integrada de processos e demandas finalísticas da SA-GTI (SOE & SEI-SP)"),
    ("🌐 179 Processos no Backlog",
     "🌐 Processos Integrados SOE & SEI"),
    ("Mapeamento de 179 processos ativos em 3 frentes de governança",
     "Mapeamento de processos e outorgas ativas em 3 frentes de governança"),
    ("Mapeamento de 179 processos ativos em 3 frentes",
     "Mapeamento de processos e outorgas ativas em 3 frentes")
]

for antigo, novo in substituicoes:
    if antigo in text:
        text = text.replace(antigo, novo)

with open(caminho_painel, "w", encoding="utf-8") as f:
    f.write(text)

print("Aba 1 saneada com sucesso: desacoplada da planilha legada e apontada para o motor do SOE & SEI-SP!")
