# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" TRANSIÇÃO DE PARADIGMA: MOTOR #6 SEI ──> PIPELINE HOT FOLDER")
print(" Desacoplamento de Sonda de Rede para Ingestão Dirigida por Eventos")
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

    # 1. Atualizar mot-6 em MOTORES_PADRAO (Sai do status ativo e passa para Pausado / Sob Demanda)
    pattern_mot6 = r'\{\s*"id":\s*"mot-6"[\s\S]*?"desc":\s*"[^"]*"\s*\}'
    novo_bloco_mot6 = '''{
                "id": "mot-6",
                "nome": "6. 📂 Ingestão SEI v7.1 (Pipeline Hot Folder)",
                "tipo": "Hot Folder / Watchdog",
                "endpoint": "C:\\\\Cockpit_GTI\\\\ingestao_sei\\\\novos_pdfs",
                "endpoint_remoto": "C:\\\\Cockpit_GTI\\\\ingestao_sei\\\\novos_pdfs",
                "freq": "Sob Demanda (Hot Folder)",
                "status": "pausado",
                "modo_resiliencia": "watchdog_hotfolder_v71",
                "desc": "Pipeline ETL por Pasta Monitorada (Watchdog). Não executa varredura de rede periódica."
        }'''
    html = re.sub(pattern_mot6, novo_bloco_mot6, html, count=1)

    # 2. Atualizar sei_pdf_etl em MOTORES_CANONICOS_V9 (Matriz de Conectores)
    pattern_canon = r'\{\s*id:\s*\'sei_pdf_etl\'[\s\S]*?detalheLocal:\s*\'[^\']*\'\s*\}'
    novo_bloco_canon = "{ id: 'sei_pdf_etl', nome: '6. 📂 Ingestão SEI v7.1 (Pipeline Hot Folder)', endpoint: 'C:\\\\Cockpit_GTI\\\\ingestao_sei\\\\novos_pdfs', fallbackTipo: 'fonte_local', detalheLocal: 'Pipeline de Ingestão por Pasta Monitorada (Watchdog Event-Driven) — Sem Sondagem HTTP' }"
    html = re.sub(pattern_canon, novo_bloco_canon, html, count=1)

    # 3. Invalidar chave de cache do localStorage
    html = html.replace('v11.0_canonico_11_motores', 'v11.1_hotfolder_sei')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[*] Arquivo atualizado: {caminho}")

print("\n[OK] Reclassificação concluída:")
print("     • Nome: 6. 📂 Ingestão SEI v7.1 (Pipeline Hot Folder)")
print("     • Tipo: Hot Folder / Watchdog")
print("     • Endpoint: C:\\Cockpit_GTI\\ingestao_sei\\novos_pdfs")
print("     • Frequência: Sob Demanda (Hot Folder)")
print("     • Status: ⚪ Pausado (Removido do ciclo ativo de 30 min)")
print("     • Cache Local: Invalidado para 'v11.1_hotfolder_sei'")

print("\n" + "=" * 70)
print(" TRANSIÇÃO CONCLUÍDA: MOTOR #6 OFICIALMENTE DESACOPLADO DA REDE!")
print("=" * 70)
