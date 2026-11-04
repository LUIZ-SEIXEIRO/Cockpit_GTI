# -*- coding: utf-8 -*-
import sys, json, time, urllib.request

candidatos_ip = ["10.20.40.212", "100.103.100.98"]
chave = "sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn"
modelo = "gemini-3.1-flash-lite"

print("=" * 70)
print(" AUDITORIA MOTOR #2: SERVIDOR ──> NEW API NO NOTEBOOK")
print(f" Alvo Primário: 10.20.40.212:3001 | Agente: {modelo}")
print("=" * 70)

# 1. Descobrir e testar a rota com o Notebook
endpoint_valido = None
mods = []

for ip in candidatos_ip:
    url_teste = f"http://{ip}:3001/v1/models"
    print(f"[*] Testando conexão com New API em {url_teste}...")
    try:
        t0 = time.time()
        req = urllib.request.Request(url_teste, headers={"Authorization": f"Bearer {chave}"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            lat = round((time.time() - t0) * 1000)
            res = json.loads(resp.read().decode("utf-8"))
            mods = [m.get("id") for m in res.get("data", [])]
            print(f"    [OK] CONEXÃO ESTABELECIDA via {ip}! Latência: {lat}ms | HTTP: {resp.status}")
            print(f"    Modelos mapeados ({len(mods)}): {mods}")
            endpoint_valido = f"http://{ip}:3001/v1"
            break
    except Exception as e:
        print(f"    [AVISO] Não conectou via {ip}: {e}")

if not endpoint_valido:
    print("\n[!] AVISO IMPORTANTE:")
    print("    1. Certifique-se de que a New API está ligada no seu notebook (teste abrindo http://localhost:3001 no navegador dele).")
    print("    2. Caso a New API esteja no Docker no notebook, garanta que a porta 3001 está mapeada (-p 3001:3000).")
    sys.exit(1)

# 2. Testar Inferência Real com o Modelo Gemini
print(f"\n[*] 2. Disparando inferência para o {modelo} via New API do notebook...")
modelo_alvo = modelo if (not mods or modelo in mods) else mods[0]
payload = {
    "model": modelo_alvo,
    "messages": [
        {"role": "system", "content": "Você é o assistente técnico de governança da SA-GTI SP-Águas."},
        {"role": "user", "content": "Emita uma confirmação de 1 linha: Motor 2 New API conectado e operacional para a SP-Águas."}
    ],
    "max_tokens": 80,
    "temperature": 0.0
}

try:
    t0 = time.time()
    req_chat = urllib.request.Request(
        f"{endpoint_valido}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_chat, timeout=20) as resp:
        lat_chat = round((time.time() - t0) * 1000)
        res_chat = json.loads(resp.read().decode("utf-8"))
        resposta = res_chat["choices"][0]["message"]["content"].strip()
        tokens = res_chat.get("usage", {}).get("total_tokens", 0)
        print(f"    [OK] Inferência concluída com sucesso em {lat_chat}ms!")
        print(f"    Resposta da IA: \"{resposta}\"")
        print(f"    Consumo: {tokens} tokens")

        # 3. Gravar no MariaDB do Servidor
        print("\n[*] 3. Gravando auditoria no MariaDB (glpidb:3306)...")
        import pymysql
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS log_inferencias_ia (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    slot_ia VARCHAR(30) NOT NULL,
                    modelo_utilizado VARCHAR(100) NOT NULL,
                    id_processo_sei VARCHAR(50) DEFAULT NULL,
                    prompt_resumo VARCHAR(255),
                    resposta_texto LONGTEXT,
                    tokens_resposta INT DEFAULT 0,
                    tempo_resposta_ms INT DEFAULT 0,
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.execute("""
                INSERT INTO log_inferencias_ia 
                (slot_ia, modelo_utilizado, id_processo_sei, prompt_resumo, resposta_texto, tokens_resposta, tempo_resposta_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, ('principal', modelo_alvo, '137.00004844/2026-21', 'Auditoria Motor 2 Notebook New API', resposta, tokens, lat_chat))
            conn.commit()
            print("    [OK] Inferência gravada no MariaDB na tabela 'log_inferencias_ia'!")
        conn.close()

except Exception as e:
    print(f"    [FALHA NA INFERÊNCIA]: {e}")

print("=" * 70)
print(" LAUDO DO MOTOR #2 CONCLUÍDO")
print("=" * 70)
