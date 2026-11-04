# -*- coding: utf-8 -*-
import sys, json, time, urllib.request

print("=" * 70)
print(" CORREÇÃO E ATIVAÇÃO DO MOTOR #2: POOL DE IAS & MARIADB")
print("=" * 70)

# 1. Criar Tabela de Auditoria no MariaDB (glpidb:3306)
print("[*] 1. Criando tabela 'log_inferencias_ia' no MariaDB local...")
try:
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
                tokens_prompt INT DEFAULT 0,
                tokens_resposta INT DEFAULT 0,
                tempo_resposta_ms INT DEFAULT 0,
                status_execucao VARCHAR(20) DEFAULT 'SUCESSO',
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        print("    [OK] Tabela 'log_inferencias_ia' criada e pronta no MariaDB!")
    conn.close()
except Exception as e:
    print(f"    [ERRO] Falha ao criar tabela no MariaDB: {e}")

# 2. Testar Autenticação com a Chave Padrão do Cockpit no New API
chave_cockpit = "sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn"
url_newapi = "http://localhost:3001/v1/models"
print(f"\n[*] 2. Testando autenticação no New API (:3001) com a chave do Cockpit...")
newapi_pronto = False
try:
    req = urllib.request.Request(url_newapi, headers={"Authorization": f"Bearer {chave_cockpit}"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        modelos_newapi = [m.get("id") for m in data.get("data", [])]
        print(f"    [OK] Chave VÁLIDA no New API! Modelos mapeados: {modelos_newapi}")
        newapi_pronto = True
except Exception as e:
    print(f"    [INFO] Chave não autorizada no New API ou canal Ollama pendente ({e}).")
    print("           (Podemos usar o endpoint nativo OpenAI do Ollama :11434/v1 como ponte direta)")

# 3. Teste de Inferência Real Direta no Ollama (OpenAI-Compatible :11434/v1)
print(f"\n[*] 3. Testando inferência real com o 'agente-geral:latest'...")
endpoint_alvo = "http://localhost:3001/v1/chat/completions" if newapi_pronto else "http://localhost:11434/v1/chat/completions"
auth_header = f"Bearer {chave_cockpit}" if newapi_pronto else "Bearer ollama"

payload = {
    "model": "agente-geral:latest",
    "messages": [
        {"role": "system", "content": "Você é o assistente técnico de governança da SA-GTI SP-Águas."},
        {"role": "user", "content": "Responda em uma única frase: Qual a função da SA-GTI na SP-Águas?"}
    ],
    "max_tokens": 80,
    "temperature": 0.0
}

try:
    t0 = time.time()
    req_chat = urllib.request.Request(
        endpoint_alvo,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": auth_header}
    )
    with urllib.request.urlopen(req_chat, timeout=15) as resp_chat:
        lat_ms = round((time.time() - t0) * 1000)
        res_json = json.loads(resp_chat.read().decode("utf-8"))
        msg_ia = res_json["choices"][0]["message"]["content"].strip()
        tokens_uso = res_json.get("usage", {}).get("total_tokens", 0)
        print(f"    [OK] Inferência concluída em {lat_ms}ms!")
        print(f"    Resposta da IA: \"{msg_ia}\"")

        # 4. Gravar a Inferência de Teste no MariaDB
        print("\n[*] 4. Gravando registro probatório da inferência no MariaDB...")
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO log_inferencias_ia 
                (slot_ia, modelo_utilizado, id_processo_sei, prompt_resumo, resposta_texto, tokens_prompt, tokens_resposta, tempo_resposta_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, ('principal', 'agente-geral:latest', '137.00004844/2026-21', 'Função da SA-GTI na SP-Águas', msg_ia, 30, tokens_uso, lat_ms))
            conn.commit()
            print("    [OK] Inferência gravada com sucesso na tabela 'log_inferencias_ia'!")
        conn.close()

except Exception as e:
    print(f"    [AVISO] Teste de inferência: {e}")

print("=" * 70)
print(" LAUDO E INTEGRAÇÃO DO MOTOR #2 CONCLUÍDOS")
print("=" * 70)
