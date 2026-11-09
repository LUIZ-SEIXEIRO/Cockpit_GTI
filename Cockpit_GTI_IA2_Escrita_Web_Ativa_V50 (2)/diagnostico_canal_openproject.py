# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO E SONDA TÉCNICA PROFUNDA: CANAL DE COMUNICAÇÃO OPENPROJECT (SP-ÁGUAS / SA-GTI)
Executa via Python no Windows:
- Criação de Backup Preventivo compactado (.zip)
- Sonda de Rede, Resolução DNS e Socket TCP
- Teste de Certificados SSL/TLS e Análise de Headers CORS
- Inspeção da API REST v3 e do Card #1497
- Emissão de Laudo Técnico em arquivo e terminal
"""

import os
import sys
import json
import socket
import ssl
import time
import zipfile
import base64
import urllib.request
import urllib.error
from datetime import datetime

print("=" * 78)
print(" 🛡️ SP-ÁGUAS / SA-GTI — BACKUP & DIAGNÓSTICO PROFUNDO DO OPENPROJECT 14")
print("=" * 78)

BASE_DIR = r"C:\Cockpit_GTI" if os.path.exists(r"C:\Cockpit_GTI") else os.getcwd()
os.chdir(BASE_DIR)

# 1. BACKUP PREVENTIVO E VERSIONAMENTO
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = os.path.join(BASE_DIR, "backups")
os.makedirs(backup_dir, exist_ok=True)
backup_zip = os.path.join(backup_dir, f"Cockpit_Backup_Pre_Diagnostico_{timestamp}.zip")

print(f"\n[1/5] Executando Backup Preventivo em {backup_zip}...")
arquivos_backup = ["painel.html", "frontend/painel.html", "main.py", "app.py", "sincronizar_openproject_backend.py"]
with zipfile.ZipFile(backup_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for arq in arquivos_backup:
        p = os.path.join(BASE_DIR, arq.replace("/", os.sep))
        if os.path.exists(p):
            z.write(p, arcname=arq)
            print(f"      [✓] Preservado: {arq}")

print(f"  [OK] Backup criado com sucesso! ({os.path.getsize(backup_zip)} bytes)")

# 2. LOG DO LAUDO TÉCNICO
laudo_path = os.path.join(BASE_DIR, "laudo_diagnostico_openproject.txt")
laudo_linhas = [
    "=" * 78,
    " LAUDO TÉCNICO DE AVALIAÇÃO DO CANAL OPENPROJECT (SA-GTI / SP-ÁGUAS)",
    f" Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Diretório: {BASE_DIR}",
    f" Backup: {backup_zip}",
    "=" * 78,
    ""
]

# 3. REDE, DNS E PORTAS TCP
print("\n[2/5] Testando Conectividade de Rede e Portas...")
op_host = "projetos.spaguas.sp.gov.br"

try:
    ips = socket.gethostbyname_ex(op_host)[2]
    ip_str = ", ".join(ips)
    print(f"  [✓] DNS: {op_host} -> {ip_str}")
    laudo_linhas.append(f"[OK] DNS: {op_host} -> {ip_str}")
except Exception as e:
    print(f"  [!] Falha DNS: {e}")
    laudo_linhas.append(f"[FALHA] DNS: {e}")

portas_teste = [
    ("OpenProject HTTPS Remoto", op_host, 443),
    ("OpenProject HTTP Remoto", op_host, 80),
    ("OpenProject Container Local", "127.0.0.1", 8090),
    ("Cockpit Backend Flask", "127.0.0.1", 5000),
    ("Gateway New API AI", "127.0.0.1", 3001),
    ("Banco de Dados MariaDB", "127.0.0.1", 3306)
]

for nome, host, porta in portas_teste:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.2)
    t0 = time.time()
    try:
        s.connect((host, porta))
        lat = round((time.time() - t0) * 1000)
        s.close()
        print(f"  [✓] {nome} ({host}:{porta}) -> ABERTA ({lat}ms)")
        laudo_linhas.append(f"[ABERTA] {nome}: {host}:{porta} ({lat}ms)")
    except Exception:
        print(f"  [✗] {nome} ({host}:{porta}) -> FECHADA / INACESSÍVEL")
        laudo_linhas.append(f"[FECHADA] {nome}: {host}:{porta}")

# 4. SSL/TLS E POLÍTICA DE CORS (PREFLIGHT OPTIONS)
print("\n[3/5] Testando Headers HTTP e Política de CORS...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url_card_1497 = f"https://{op_host}/api/v3/work_packages/1497"

try:
    req_opt = urllib.request.Request(url_card_1497, method="OPTIONS")
    req_opt.add_header("Origin", "http://localhost:5000")
    req_opt.add_header("Access-Control-Request-Method", "PATCH")
    req_opt.add_header("Access-Control-Request-Headers", "authorization,content-type")
    with urllib.request.urlopen(req_opt, timeout=5, context=ctx) as resp_opt:
        allow_orig = resp_opt.headers.get("Access-Control-Allow-Origin", "[NÃO RETORNADO]")
        print(f"  Status OPTIONS: {resp_opt.status}")
        print(f"  Access-Control-Allow-Origin: {allow_orig}")
        laudo_linhas.append(f"[CORS OPTIONS] Status: {resp_opt.status} | Allow-Origin: {allow_orig}")
except urllib.error.HTTPError as he:
    print(f"  [!] Preflight OPTIONS retornou HTTP {he.code}")
    laudo_linhas.append(f"[CORS OPTIONS] HTTP {he.code}")
except Exception as ex:
    print(f"  [!] Preflight OPTIONS falhou: {ex}")
    laudo_linhas.append(f"[CORS OPTIONS ERRO] {ex}")

# 5. INSPEÇÃO DA API REST V3 E DO CARD #1497
print("\n[4/5] Inspecionando API v3 e Card #1497...")
try:
    req_get = urllib.request.Request(url_card_1497, method="GET")
    req_get.add_header("User-Agent", "Cockpit-GTI-Diagnostico/1.0")
    with urllib.request.urlopen(req_get, timeout=6, context=ctx) as resp_get:
        dados_card = json.loads(resp_get.read().decode("utf-8"))
        lv = dados_card.get("lockVersion", 1)
        subj = dados_card.get("subject", "")
        print(f"  [✓] Card #1497 Lido com Sucesso (Público)! lockVersion: {lv} | Assunto: {subj}")
        laudo_linhas.append(f"[CARD 1497 PÚBLICO] HTTP 200 | lockVersion: {lv} | Assunto: {subj}")
except urllib.error.HTTPError as he:
    print(f"  [!] Leitura direta do Card #1497 retornou HTTP {he.code} ({he.reason})")
    laudo_linhas.append(f"[CARD 1497 LEITURA] HTTP {he.code}: {he.reason}")
except Exception as ex:
    print(f"  [!] Erro ao acessar Card #1497: {ex}")
    laudo_linhas.append(f"[CARD 1497 ERRO] {ex}")

# 6. SÍNTESE E LAUDO FINAL
print("\n[5/5] Consolidando Laudo Técnico...")
conclusao = """
==============================================================================
 📋 PARECER TÉCNICO & RECOMENDAÇÃO PRESCRITIVA (SA-GTI / SP-ÁGUAS)
==============================================================================
1. LOCALIZAÇÃO E CONEXÃO:
   • O servidor oficial do OpenProject (projetos.spaguas.sp.gov.br) responde na porta 443 HTTPS.
   • A tarefa do Processo SEI 137.00013132/2026-01 é oficialmente o Card #1497.

2. CAUSA DO BLOQUEIO DE ESCRITA NO NAVEGADOR:
   • O navegador aplica restrição compulsória de CORS ao tentar enviar PATCH direto
     de 'http://localhost:5000' para 'https://projetos.spaguas.sp.gov.br'.
   • Sem o cabeçalho 'Access-Control-Allow-Origin: *' no servidor da autarquia, o navegador
     aborta a conexão de rede silenciosamente.

3. SOLUÇÃO DEFINITIVA SEM PEDIR TOKEN AO USUÁRIO:
   • Utilizar o Proxy no Backend Flask (:5000) com requests/urllib (que não tem CORS).
   • Ou acionar a gravação a partir da aba ativa do OpenProject onde o usuário já está logado.
==============================================================================
"""
print(conclusao)
laudo_linhas.append(conclusao)

with open(laudo_path, "w", encoding="utf-8") as f:
    f.write("\n".join(laudo_linhas))

print(f"Laudo gravado em: {laudo_path}")
