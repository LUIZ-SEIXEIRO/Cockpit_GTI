# -*- coding: utf-8 -*-
"""
==============================================================================
 SP-AGUAS / SA-GTI -- DESBLOQUEIO DE FIREWALL & TESTE DA IA 2 (PYTHON)
==============================================================================
Executa sem qualquer incompatibilidade de encoding de PowerShell:
1. Identifica os IPs da maquina local
2. Configura regras de entrada no Windows Firewall para portas 3001, 5000 e 11434 via netsh
3. Verifica portas escutando localmente via netstat
4. Testa conectividade TCP Socket na porta 3001 (10.20.40.212 e 127.0.0.1)
5. Dispara requisicao HTTP real para a IA 2 com o token e modelo llama3.2:1b
==============================================================================
"""

import os
import sys
import json
import socket
import ssl
import subprocess
import urllib.request
import urllib.error

TOKEN = "sk-GxdEHwXjAPXW50uuBVeDLAEeSXdt6kJfcduffPsjBnmsRs3H"
MODELO = "llama3.2:1b"
HOST_REDE = "10.20.40.212"
PORTA_IA = 3001

print("=" * 78)
print(" SP-AGUAS / SA-GTI -- DESBLOQUEIO DE FIREWALL & DIAGNOSTICO DA IA 2")
print(f" Agente Alvo: {MODELO} @ http://{HOST_REDE}:{PORTA_IA}/v1")
print("=" * 78)

# 1. Identificar IPs desta maquina
print("\n[1/5] Identificando IPs desta maquina...")
try:
    hostname = socket.gethostname()
    ips = socket.gethostbyname_ex(hostname)[2]
    e_o_host = False
    for ip in ips:
        if ip == HOST_REDE:
            e_o_host = True
            print(f"  [OK] IP {ip} DETECTADO: Esta maquina e o host {HOST_REDE}!")
        else:
            print(f"  * IP Local detectado: {ip}")
    if not e_o_host:
        print(f"  [i] Esta maquina nao possui o IP {HOST_REDE} configurado diretamente.")
        print(f"      Se o host {HOST_REDE} for outra maquina (ex: Desktop Miniservidor),")
        print(f"      a comunicacao sera feita via rede local.")
except Exception as e:
    print(f"  [i] Nao foi possivel listar todos os IPs: {e}")

# 2. Configurar Regras de Entrada no Windows Firewall via netsh
print("\n[2/5] Configurando Regras de Entrada no Windows Firewall...")
portas_firewall = [
    ("Cockpit_GTI_NewAPI_3001", 3001),
    ("Cockpit_GTI_Flask_5000", 5000),
    ("Cockpit_GTI_Ollama_11434", 11434)
]

for nome_regra, porta in portas_firewall:
    cmd = f'netsh advfirewall firewall add rule name="{nome_regra}" dir=in action=allow protocol=TCP localport={porta}'
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if "OK" in res.stdout or res.returncode == 0:
            print(f"  [OK] Firewall: Porta {porta} TCP liberada com sucesso!")
        else:
            print(f"  [i] Firewall porta {porta}: {res.stdout.strip() or 'Regra ja existente ou requer permissao de Admin'}")
    except Exception as e:
        print(f"  [i] Erro ao configurar firewall porta {porta}: {e}")

# 3. Verificar o que esta escutando na porta 3001
print("\n[3/5] Verificando se algum processo escuta na porta 3001...")
try:
    cmd_ns = "netstat -ano | findstr :3001"
    res_ns = subprocess.run(cmd_ns, shell=True, capture_output=True, text=True)
    saida = res_ns.stdout.strip()
    if saida:
        print("  [OK] Processo(s) detectado(s) na porta 3001:")
        for linha in saida.splitlines():
            print(f"      {linha}")
        if "127.0.0.1:3001" in saida and "0.0.0.0:3001" not in saida:
            print("  [ALERTA DE BINDING]: O servico esta escutando APENAS em 127.0.0.1 (localhost)!")
            print("  Isso significa que conexoes vindas pelo IP de rede (10.20.40.212) serao rejeitadas.")
            print("  Solucao: Inicie o New API com binding 0.0.0.0.")
        elif "0.0.0.0:3001" in saida or ":::3001" in saida:
            print("  [OK BINDING]: Servico escutando em 0.0.0.0 (todas as interfaces de rede)!")
    else:
        print("  [X] NENHUM processo escutando na porta 3001 nesta maquina local.")
        print("      * Se o New API estiver rodando no Notebook, confirme se o Notebook esta ligado na mesma rede.")
        print("      * Se o New API deveria rodar no Miniservidor, inicie o aplicativo/container do New API.")
except Exception as e:
    print(f"  [i] Erro ao executar netstat: {e}")

# 4. Testar Conectividade TCP Socket na porta 3001
print("\n[4/5] Testando Conectividade de Rede (TCP Socket)...")
alvos = [
    (HOST_REDE, PORTA_IA, f"IP de Rede ({HOST_REDE}:{PORTA_IA})"),
    ("100.103.100.98", PORTA_IA, "IP Tailscale Notebook (100.103.100.98:3001)"),
    ("127.0.0.1", PORTA_IA, f"Loopback Local (127.0.0.1:{PORTA_IA})")
]

endpoint_ok = None
for h, p, rotulo in alvos:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.5)
    try:
        s.connect((h, p))
        s.close()
        print(f"  [OK] {rotulo}: CONEXAO ESTABELECIDA COM SUCESSO (Porta Aberta)!")
        if not endpoint_ok:
            endpoint_ok = f"http://{h}:{p}/v1"
    except Exception as e:
        print(f"  [X] {rotulo}: CONEXAO RECUSADA OU TIMEOUT ({e})")

# 5. Testar Chamada HTTP Real a IA 2 com Token e Modelo llama3.2:1b
print(f"\n[5/5] Testando Chamada HTTP Real a IA 2 ({MODELO})...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls_teste = []
if endpoint_ok:
    urls_teste.append(f"{endpoint_ok}/chat/completions")
urls_teste.append(f"http://{HOST_REDE}:{PORTA_IA}/v1/chat/completions")
urls_teste.append("http://100.103.100.98:3001/v1/chat/completions")
urls_teste.append(f"http://127.0.0.1:{PORTA_IA}/v1/chat/completions")

# Remove duplicatas preservando ordem
urls_unicas = []
for u in urls_teste:
    if u not in urls_unicas:
        urls_unicas.append(u)

ia_respondeu = False
for url in urls_unicas:
    print(f"  [*] Enviando requisicao POST para: {url}...")
    payload = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": "Voce e a IA 2 -- Orquestracao da SA-GTI SP-Aguas."},
            {"role": "user", "content": "Emita confirmacao de uma linha: IA 2 ONLINE E OPERACIONAL."}
        ],
        "temperature": 0.0,
        "max_tokens": 40
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            if resp.status == 200:
                dados = json.loads(resp.read().decode("utf-8"))
                conteudo = dados["choices"][0]["message"]["content"].strip()
                print(f"  [OK] RESPOSTA RECEBIDA DA IA 2 ({MODELO})!")
                print(f"      Mensagem: \"{conteudo}\"")
                ia_respondeu = True
                break
    except urllib.error.HTTPError as e:
        print(f"  [!] HTTP Error {e.code}: {e.reason}")
        try:
            detalhes = e.read().decode("utf-8")
            print(f"      Detalhes da API: {detalhes[:200]}")
        except Exception:
            pass
    except Exception as e:
        print(f"  [!] Falha de conexao: {e}")

print("\n" + "=" * 78)
if ia_respondeu:
    print(" [SUCESSO TOTAL] A IA 2 ESTA OPERACIONAL E RESPONDENDO COM O TOKEN REAL!")
    print(" Agora voce pode rodar: python sincronizar_openproject_backend.py")
else:
    print(" [DIAGNOSTICO CONCLUSIVO]:")
    print(f" 1. Se a Porta {PORTA_IA} deu CONEXAO RECUSADA:")
    print("    - O servico New API nao esta rodando, ou esta rodando em outra maquina.")
    print(" 2. Verifique onde o New API esta aberto:")
    print("    - Se estiver no NOTEBOOK, execute 'ipconfig' no notebook para descobrir o IP dele.")
    print("    - Se o notebook for por exemplo 10.20.40.150, o endpoint sera http://10.20.40.150:3001/v1.")
    print(" 3. Se estiver no Miniservidor (Desktop):")
    print("    - Inicie o New API no desktop.")
print("=" * 78)
