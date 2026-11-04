# -*- coding: utf-8 -*-
import sys, json, time, urllib.request

print("=" * 70)
print(" AUDITORIA TÉCNICA DO MOTOR #1: SEI-SP & DIÁRIO OFICIAL (DOE-SP)")
print("=" * 70)

# 1. Teste de Handshake HTTPS ao vivo com o DOE-SP
url_doe = "https://www.doe.sp.gov.br"
print(f"[*] 1. Testando conexão com portal oficial ({url_doe})...")
try:
    t0 = time.time()
    req = urllib.request.Request(url_doe, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        lat = round((time.time() - t0) * 1000)
        print(f"    [OK] DOE-SP ONLINE! Status HTTP: {resp.status} | Latência: {lat}ms")
except Exception as e:
    print(f"    [AVISO] Conexão externa direta: {e}")

# 2. Teste da API Flask Local (:5000)
url_flask = "http://127.0.0.1:5000/api/v1/feeds/publicacoes"
print(f"\n[*] 2. Consultando endpoint de feeds no Flask local ({url_flask})...")
try:
    with urllib.request.urlopen(url_flask, timeout=3) as resp:
        dados = json.loads(resp.read().decode("utf-8"))
        itens = dados.get("itens", [])
        doe_itens = [i for i in itens if i.get("fonte") == "DOE-SP"]
        print(f"    [OK] Backend Flask ativo! Total de feeds: {len(itens)} (DOE-SP: {len(doe_itens)})")
except Exception as e:
    print(f"    [INFO] Flask não respondeu na rota de feeds: {e}")

# 3. Teste Direto no Banco de Dados MariaDB (glpidb:3306)
print(f"\n[*] 3. Auditando tabelas no MariaDB local (glpidb na porta 3306)...")
try:
    import pymysql
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        # Checar processos_sei
        cur.execute("SHOW TABLES LIKE 'processos_sei'")
        if cur.fetchone():
            cur.execute("SELECT COUNT(*) FROM processos_sei")
            total_procs = cur.fetchone()[0]
            print(f"    [OK] Tabela 'processos_sei': {total_procs} processos registrados.")
        else:
            print("    [!] Tabela 'processos_sei' não encontrada no banco.")

        # Checar feed_publicacoes_externas
        cur.execute("SHOW TABLES LIKE 'feed_publicacoes_externas'")
        if cur.fetchone():
            cur.execute("SELECT fonte, COUNT(*) FROM feed_publicacoes_externas GROUP BY fonte")
            for fonte, total in cur.fetchall():
                print(f"    [OK] Tabela 'feed_publicacoes_externas' -> Fonte {fonte}: {total} registros.")
        else:
            print("    [!] Tabela 'feed_publicacoes_externas' não encontrada no banco.")
    conn.close()
except ImportError:
    print("    [INFO] pymysql não instalado no ambiente (execute: pip install pymysql).")
except Exception as e:
    print(f"    [AVISO] Conexão MariaDB: {e}")

print("=" * 70)
print(" LAUDO DO MOTOR #1 CONCLUÍDO")
print("=" * 70)
