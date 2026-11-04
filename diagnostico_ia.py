# -*- coding: utf-8 -*-
import sys, json, time, urllib.request

print("=" * 70)
print(" DIAGNÓSTICO: MOTOR #2 (GATEWAY NEW API :3001 / OLLAMA :11434)")
print("=" * 70)

# 1. Testar New API Gateway (:3001)
url_newapi = "http://localhost:3001/v1/models"
print(f"[*] 1. Testando Gateway New API ({url_newapi})...")
try:
    req = urllib.request.Request(url_newapi, headers={"Authorization": "Bearer sk-teste"})
    with urllib.request.urlopen(req, timeout=2) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"    [OK] New API ONLINE na porta 3001! Modelos disponíveis: {len(data.get('data', []))}")
except Exception as e:
    print(f"    [INCONSISTÊNCIA CONFIRMADA] New API inacessível na porta 3001: {e}")

# 2. Testar Ollama Local (:11434)
url_ollama = "http://localhost:11434/api/tags"
print(f"\n[*] 2. Testando Ollama Nativo Local ({url_ollama})...")
try:
    with urllib.request.urlopen(url_ollama, timeout=2) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        modelos = [m.get("name") for m in data.get("models", [])]
        print(f"    [OK] Ollama ONLINE na porta 11434!")
        print(f"    Modelos locais instalados ({len(modelos)}): {modelos}")
except Exception as e:
    print(f"    [AVISO] Ollama inacessível na porta 11434: {e}")

# 3. Verificar Tabela de Auditoria de IA no MariaDB
print(f"\n[*] 3. Verificando tabela de logs de IA no MariaDB (glpidb:3306)...")
try:
    import pymysql
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES LIKE 'log_inferencias_ia'")
        if cur.fetchone():
            cur.execute("SELECT COUNT(*) FROM log_inferencias_ia")
            print(f"    [OK] Tabela 'log_inferencias_ia' ativa com {cur.fetchone()[0]} registros.")
        else:
            print("    [!] Tabela 'log_inferencias_ia' NÃO existe no MariaDB (inferências não estão sendo auditadas no banco).")
    conn.close()
except Exception as e:
    print(f"    [AVISO] MariaDB: {e}")

print("=" * 70)
print(" DIAGNÓSTICO CONCLUÍDO")
print("=" * 70)
