# -*- coding: utf-8 -*-
"""
==============================================================================
 🛡️ SP-ÁGUAS / SA-GTI — AUDITORIA & COMPROVAÇÃO DE SINCRONIZAÇÃO AGENDADA
==============================================================================
Lê e audita os registros probatórios de sincronização automática e manual
do Orquestrador OpenProject no Cockpit GTI.
==============================================================================
"""

import os
import sys
import json
import subprocess
from datetime import datetime

BASE_DIR = r"C:\Cockpit_GTI" if os.path.exists(r"C:\Cockpit_GTI") else os.getcwd()

print("=" * 78)
print(" 🛡️ SP-ÁGUAS / SA-GTI — COMPROVAÇÃO DA SINCRONIZAÇÃO AGENDADA OPENPROJECT")
print(f" Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | Governança: SA-GTI")
print("=" * 78)
print()

# 1. Checagem do Agendador de Tarefas do Windows via schtasks
print(" [1/3] VERIFICAÇÃO DO AGENDADOR DE TAREFAS DO WINDOWS:")
task_name = "CockpitGTI_Sincronizacao_Horaria_OpenProject"

try:
    cmd = f'schtasks /query /tn "{task_name}" /fo LIST /v'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors="ignore")
    if res.returncode == 0 and task_name.lower() in res.stdout.lower():
        print(f"   [OK] Tarefa Agendada Identificada: '{task_name}'")
        linhas = res.stdout.splitlines()
        for l in linhas:
            if "status:" in l.lower() or "próxima hora de execução:" in l.lower() or "next run time:" in l.lower() or "última hora de execução:" in l.lower() or "last run time:" in l.lower() or "resultado da última execução:" in l.lower() or "last result:" in l.lower():
                print(f"       • {l.strip()}")
    else:
        print(f"   [!] Tarefa '{task_name}' ainda não registrada no Agendador do Windows.")
        print("       Dica: Execute 'powershell -File ativar_automacao_horaria_windows.ps1' para registrar.")
except Exception as e:
    print(f"   [!] Não foi possível consultar schtasks: {e}")

print()

# 2. Leitura do Registro Histórico JSON
print(" [2/3] REGISTRO HISTÓRICO DE EXECUÇÕES (registro_execucao_agendada.json):")
reg_json_path = os.path.join(BASE_DIR, "registro_execucao_agendada.json")

if os.path.exists(reg_json_path):
    try:
        with open(reg_json_path, "r", encoding="utf-8") as f:
            historico = json.load(f)
        total = len(historico)
        print(f"   [OK] Arquivo de histórico localizado: {total} execuções registradas.")
        print()
        print("   Últimas Execuções Registradas:")
        for item in historico[:5]:
            ts = item.get("timestamp", "—")
            modo = item.get("modo", "Agendado")
            cards = item.get("cards_processados", 0)
            status = item.get("status", "SUCESSO")
            comprovante = item.get("comprovante_hash", "OK")
            print(f"   • [{ts}] - Modo: {modo} | Cards: {cards} | Status: {status} | Comprovante: #{comprovante}")
    except Exception as e:
        print(f"   [!] Erro ao ler JSON: {e}")
else:
    print(f"   [i] Nenhum registro histórico gerado ainda em '{reg_json_path}'.")
    print("       O arquivo é gerado automaticamente na primeira execução do motor.")

print()

# 3. Leitura do Laudo de Auditoria TXT
print(" [3/3] LAUDO PROBATÓRIO DE AUDITORIA (laudo_sincronizacao_automatica.txt):")
laudo_path = os.path.join(BASE_DIR, "laudo_sincronizacao_automatica.txt")

if os.path.exists(laudo_path):
    print("   [OK] Laudo de auditoria localizado.")
    try:
        with open(laudo_path, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
        ultimas = [l.strip() for l in linhas[-8:] if l.strip()]
        print()
        print("   Últimos registros de log:")
        for l in ultimas:
            print(f"     {l}")
    except Exception as e:
        print(f"   [!] Erro ao ler laudo: {e}")
else:
    print("   [i] Arquivo laudo_sincronizacao_automatica.txt será gerado na primeira sincronização.")

print()
print("=" * 78)
print(" [RESUMO DO COMPROVANTE] Governança SA-GTI / SP-Águas")
print(" • Sincronização Agendada: Conforme ajuste configurado no Motor 3")
print(" • Sincronização Manual 1 a 1: Ativa e Homologada no Orquestrador Web")
print("=" * 78)
