# -*- coding: utf-8 -*-
import os, re, json, time, urllib.request, urllib.error

endpoint_base = "http://10.20.40.212:3001/v1"
chaves_para_testar = [
    ("Nova Chave Enviada", "sk-8QfgiQ39Ob3TrWypXs5MFneX80DEqUYkrgcXiiG2GRXDSasv"),
    ("API KEY LASS - SP ÁGUAS", "sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn")
]
modelo = "gemini-2.5-flash"

print("=" * 70)
print(f" VALIDAÇÃO MOTOR #2: {modelo.upper()} VIA NEW API (10.20.40.212:3001)")
print(" Testando chaves disponíveis e gravando no MariaDB (glpidb:3306)")
print("=" * 70)

chave_operacional = None
nome_operacional = None

# 1. Testar qual chave possui acesso ao gemini-2.5-flash
print("[*] 1. Testando permissões de modelo para as chaves na New API...")
for nome, k in chaves_para_testar:
    url_models = f"{endpoint_base}/models"
    try:
        req = urllib.request.Request(url_models, headers={"Authorization": f"Bearer {k}"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            mods = [m.get("id") for m in res.get("data", [])]
            print(f"    [{nome}]: {len(mods)} modelo(s) liberado(s) -> {mods}")
            if modelo in mods or not mods or len(mods) > 0:
                chave_operacional = k
                nome_operacional = nome
                if modelo in mods:
                    break
    except Exception as e:
        print(f"    [{nome}]: {e}")

if not chave_operacional:
    chave_operacional = chaves_para_testar[0][1]
    nome_operacional = chaves_para_testar[0][0]

print(f"\n[*] Chave selecionada para a chamada: {nome_operacional}")

# 2. Disparar inferência real com o Gemini 2.5 Flash
print(f"[*] 2. Disparando inferência para o {modelo} em {endpoint_base}/chat/completions...")
payload = {
    "model": modelo,
    "messages": [
        {"role": "system", "content": "Você é o assistente técnico de governança da SA-GTI SP-Águas."},
        {"role": "user", "content": "Emita uma confirmação de 1 linha: Motor 2 New API com Gemini 2.5 Flash validado e operacional para a SP-Águas."}
    ],
    "max_tokens": 80,
    "temperature": 0.0
}

try:
    t0 = time.time()
    req_chat = urllib.request.Request(
        f"{endpoint_base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave_operacional}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_chat, timeout=20) as resp:
        lat = round((time.time() - t0) * 1000)
        res_chat = json.loads(resp.read().decode("utf-8"))
        resposta = res_chat["choices"][0]["message"]["content"].strip()
        tokens = res_chat.get("usage", {}).get("total_tokens", 0)
        print(f"    [OK] RESPOSTA DA NUVEM RECEBIDA EM {lat}ms! HTTP: {resp.status}")
        print(f"    Resposta da IA: \"{resposta}\"")
        print(f"    Consumo real: {tokens} tokens")

        # 3. Gravar e auditar no MariaDB do Servidor
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
                    status_execucao VARCHAR(20) DEFAULT 'SUCESSO',
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.execute("""
                INSERT INTO log_inferencias_ia 
                (slot_ia, modelo_utilizado, id_processo_sei, prompt_resumo, resposta_texto, tokens_resposta, tempo_resposta_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, ('principal', modelo, '137.00004844/2026-21', 'Auditoria Motor 2 Gemini 2.5 Flash', resposta, tokens, lat))
            conn.commit()
            print("    [OK] Inferência gravada no MariaDB na tabela 'log_inferencias_ia'!")

            # Consulta probatória
            cur.execute("SELECT id, slot_ia, modelo_utilizado, tempo_resposta_ms, tokens_resposta, DATE_FORMAT(data_hora, '%d/%m/%Y %H:%i:%s') FROM log_inferencias_ia ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            print(f"\n    [REGISTRO PROBATÓRIO NO MARIADB]:")
            print(f"     #ID {row[0]} | {row[5]} | Modelo: {row[2]} | Latência: {row[3]}ms | Tokens: {row[4]}")
        conn.close()

        # 4. Atualizar o Cockpit (painel.html) com a chave funcional
        print(f"\n[*] 4. Atualizando Cockpit com a chave funcional ({nome_operacional})...")
        paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]
        for p in paths:
            if not os.path.exists(p):
                continue
            with open(p, "r", encoding="utf-8") as f:
                c = f.read()
            norm = c.replace("\r\n", "\n")
            norm = norm.replace("STORAGE_KEY_POOL_3_IAS = 'sagti_pool_tres_ias_v95';", "STORAGE_KEY_POOL_3_IAS = 'sagti_pool_tres_ias_v97';")
            norm = norm.replace("STORAGE_KEY_POOL_3_IAS = 'sagti_pool_tres_ias_v96';", "STORAGE_KEY_POOL_3_IAS = 'sagti_pool_tres_ias_v97';")
            norm = re.sub(r"var keyPadrao = '[^']+';", f"var keyPadrao = '{chave_operacional}';", norm)
            norm = re.sub(r"var agentePadrao = '[^']+';", f"var agentePadrao = '{modelo}';", norm)
            final = norm.replace("\n", "\r\n") if "\r\n" in c else norm
            with open(p, "w", encoding="utf-8") as f:
                f.write(final)
            print(f"    [OK] Cockpit atualizado em {p}!")

except urllib.error.HTTPError as e:
    corpo = e.read().decode("utf-8")
    print(f"    [HTTP {e.code}] Detalhe da New API: {corpo}")
    print("    -> Lembre-se de clicar em [Save changes] na tela do New API do notebook!")
except Exception as e:
    print(f"    [ERRO]: {e}")

print("=" * 70)
print(" LAUDO DO MOTOR #2 CONCLUÍDO")
print("=" * 70)
