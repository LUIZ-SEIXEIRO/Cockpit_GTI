# -*- coding: utf-8 -*-
import sys, json, time, urllib.request

print("=" * 70)
print(" AUDITORIA TÉCNICA DO MOTOR #2: GATEWAY NEW API (:3001)")
print(" Credencial: API KEY LASS - SP ÁGUAS | Agente: gemini-3.1-flash-lite")
print("=" * 70)

chave_api = "sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn"
url_models = "http://localhost:3001/v1/models"
url_chat = "http://localhost:3001/v1/chat/completions"

# 1. Testar o Catálogo de Modelos do New API
print("[*] 1. Consultando catálogo oficial de modelos em http://localhost:3001/v1/models...")
modelos_disponiveis = []
try:
    t0 = time.time()
    req_models = urllib.request.Request(
        url_models,
        headers={"Authorization": f"Bearer {chave_api}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_models, timeout=5) as resp:
        lat_models = round((time.time() - t0) * 1000)
        res_models = json.loads(resp.read().decode("utf-8"))
        modelos_disponiveis = [m.get("id") for m in res_models.get("data", [])]
        print(f"    [OK] New API ONLINE! Status HTTP: {resp.status} | Latência: {lat_models}ms")
        print(f"    Modelos mapeados ({len(modelos_disponiveis)}): {modelos_disponiveis}")
except Exception as e:
    print(f"    [AVISO] Falha ao listar modelos no New API: {e}")
    print("           (Verifique se a New API está rodando no localhost:3001 ou no IP do notebook)")

# 2. Testar Inferência Real com o Modelo gemini-3.1-flash-lite
print("\n[*] 2. Disparando chamada real de inferência (gemini-3.1-flash-lite)...")
modelo_teste = "gemini-3.1-flash-lite"
if modelos_disponiveis and modelo_teste not in modelos_disponiveis:
    # Se o modelo exato tiver outro nome no canal (ex: gemini-2.0-flash), usamos o primeiro disponível
    print(f"    [INFO] '{modelo_teste}' não listado diretamente. Usando canal ativo: '{modelos_disponiveis[0]}'")
    modelo_teste = modelos_disponiveis[0]

payload_chat = {
    "model": modelo_teste,
    "messages": [
        {"role": "system", "content": "Você é o assistente técnico de governança da SA-GTI SP-Águas."},
        {"role": "user", "content": "Emita uma confirmação de 1 linha: Motor 2 New API auditado e operacional para a SA-GTI."}
    ],
    "max_tokens": 80,
    "temperature": 0.0
}

inferencia_ok = False
resposta_texto = ""
tokens_uso = 0
lat_chat = 0

try:
    t0 = time.time()
    req_chat = urllib.request.Request(
        url_chat,
        data=json.dumps(payload_chat).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave_api}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_chat, timeout=15) as resp:
        lat_chat = round((time.time() - t0) * 1000)
        res_chat = json.loads(resp.read().decode("utf-8"))
        resposta_texto = res_chat["choices"][0]["message"]["content"].strip()
        tokens_uso = res_chat.get("usage", {}).get("total_tokens", 0)
        print(f"    [OK] Inferência concluída em {lat_chat}ms! HTTP: {resp.status}")
        print(f"    Resposta da IA: \"{resposta_texto}\"")
        print(f"    Consumo real: {tokens_uso} tokens")
        inferencia_ok = True
except Exception as e:
    print(f"    [FALHA DE INFERÊNCIA]: {e}")

# 3. Validar e Gravar no Banco de Dados MariaDB (glpidb:3306)
print("\n[*] 3. Validando persistência de auditoria no MariaDB (glpidb na porta 3306)...")
try:
    import pymysql
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        # Garantir tabela criada
        cur.execute("""
            CREATE TABLE IF NOT EXISTS log_inferencias_ia (
                id INT AUTO_INCREMENT PRIMARY KEY,
                slot_ia VARCHAR(30) NOT NULL,
                modelo_utilizado VARCHAR(100) NOT NULL,
                id_processo_sei VARCHAR(50) DEFAULT NULL,
                prompt_resumo VARCHAR(255),
                resposta_texto LONGTEXT,
                tokens_prompt INT DEFAULT 0,
                tokens_resposta INT DEFAULT 0,
                tempo_resposta_ms INT DEFAULT 0,
                status_execucao VARCHAR(20) DEFAULT 'SUCESSO',
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        if inferencia_ok:
            cur.execute("""
                INSERT INTO log_inferencias_ia 
                (slot_ia, modelo_utilizado, id_processo_sei, prompt_resumo, resposta_texto, tokens_prompt, tokens_resposta, tempo_resposta_ms, status_execucao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ('principal', modelo_teste, '137.00004844/2026-21', 'Auditoria Motor 2 New API', resposta_texto, 35, tokens_uso, lat_chat, 'SUCESSO'))
            conn.commit()
            print("    [OK] Registro de inferência inserido com sucesso na tabela 'log_inferencias_ia'!")

        # Leitura probatória do banco
        cur.execute("SELECT id, slot_ia, modelo_utilizado, tempo_resposta_ms, tokens_resposta, DATE_FORMAT(data_hora, '%d/%m/%Y %H:%i:%s') FROM log_inferencias_ia ORDER BY id DESC LIMIT 3")
        linhas = cur.fetchall()
        print("\n    [REGISTROS AUDITADOS NO MARIADB]:")
        for lid, slot, mod, tempo, toks, dt in linhas:
            print(f"     #ID {lid} | {dt} | Slot: {slot} | Modelo: {mod} | Latência: {tempo}ms | Tokens: {toks}")

    conn.close()
except Exception as e:
    print(f"    [AVISO BANCO DE DADOS]: {e}")

print("=" * 70)
print(" LAUDO DO MOTOR #2 CONCLUÍDO")
print("=" * 70)
