# -*- coding: utf-8 -*-
import os, json, pymysql

# 1. CONEXÃO COM O MARIADB LOCAL
conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4'
)
cur = conn.cursor()

# 2. CRIAR A TABELA OFICIAL DE PROCESSOS SEI
cur.execute('''
CREATE TABLE IF NOT EXISTS processos_sei (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_processo VARCHAR(50) NOT NULL UNIQUE,
    prefixo_orgao VARCHAR(20),
    tipo_processo VARCHAR(255),
    especificacao TEXT,
    interessados VARCHAR(255),
    dias_ultima_mov INT DEFAULT 0,
    faixa_aging VARCHAR(50),
    farol_criticidade VARCHAR(50),
    marcadores_institucionais VARCHAR(255),
    responsavel_tecnico VARCHAR(150),
    eixo_gestao VARCHAR(100),
    bucket_openproject VARCHAR(100),
    status_openproject VARCHAR(50),
    classificacao_risco VARCHAR(50),
    data_carga_etl DATE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''')
print("1. Tabela processos_sei criada/verificada no MariaDB com sucesso!")

# 3. EXTRAIR OS PROCESSOS DO ARQUIVO E INGERIR VIA UPSERT NO BANCO
caminho_painel = os.path.join(os.getcwd(), "frontend", "painel.html")
if not os.path.exists(caminho_painel):
    caminho_painel = os.path.join(os.getcwd(), "painel.html")

with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = text.find('PROCESSOS = [')
end = text.find('];', pos)
raw_json = text[pos+len('PROCESSOS = '):end+1]
procs = json.loads(raw_json)

sql_insert = '''
INSERT INTO processos_sei (
    id_processo, prefixo_orgao, tipo_processo, especificacao, interessados,
    dias_ultima_mov, faixa_aging, farol_criticidade, marcadores_institucionais,
    responsavel_tecnico, eixo_gestao, bucket_openproject, status_openproject,
    classificacao_risco, data_carga_etl
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    tipo_processo=VALUES(tipo_processo),
    especificacao=VALUES(especificacao),
    dias_ultima_mov=VALUES(dias_ultima_mov),
    faixa_aging=VALUES(faixa_aging),
    farol_criticidade=VALUES(farol_criticidade),
    responsavel_tecnico=VALUES(responsavel_tecnico),
    eixo_gestao=VALUES(eixo_gestao),
    bucket_openproject=VALUES(bucket_openproject),
    status_openproject=VALUES(status_openproject);
'''

total_inseridos = 0
for p in procs:
    try:
        dias = int(p.get('Dias_Ultima_Mov', 0) or 0)
    except:
        dias = 0

    cur.execute(sql_insert, (
        p.get('ID_Processo'),
        p.get('Prefixo_Orgao', '137'),
        p.get('Tipo_Processo', ''),
        p.get('Especificacao', ''),
        p.get('Interessados', ''),
        dias,
        p.get('Faixa_Aging', 'Normal'),
        p.get('Farol_Criticidade', '4 - Fluxo Normal'),
        p.get('Marcadores_Institucionais', ''),
        p.get('Responsavel_Tecnico', ''),
        p.get('Eixo_Gestao', 'Rotina Operacional'),
        p.get('Bucket_OpenProject', ''),
        p.get('Status_OpenProject', 'Ativo'),
        p.get('Classificacao_Risco', 'Baixo'),
        '2026-09-22'
    ))
    total_inseridos += 1

conn.commit()
print(f"2. {total_inseridos} processos do SEI ingeridos com sucesso no MariaDB!")

# 4. REGISTRAR A ROTA DE CONSULTA AO VIVO NO main.py
caminho_main = os.path.join(os.getcwd(), "main.py")
if os.path.exists(caminho_main):
    with open(caminho_main, "r", encoding="utf-8") as f:
        conteudo_main = f.read()

    if "/api/v1/processos/estatisticas" not in conteudo_main:
        bloco_api_procs = '''

# --- ROTA DE CONSULTA AO VIVO DO ACERVO DE PROCESSOS (MARIADB) ---
@app.route('/api/v1/processos/estatisticas')
def estatisticas_processos_vivos():
    import pymysql
    try:
        conn = pymysql.connect(
            host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_processos,
                    SUM(CASE WHEN eixo_gestao LIKE '%Rotina%' THEN 1 ELSE 0 END) as total_rotina,
                    SUM(CASE WHEN eixo_gestao LIKE '%Esteira%' THEN 1 ELSE 0 END) as total_esteira,
                    SUM(CASE WHEN eixo_gestao LIKE '%Portfólio%' OR eixo_gestao LIKE '%Portfolio%' THEN 1 ELSE 0 END) as total_portfolio,
                    SUM(CASE WHEN farol_criticidade LIKE '%1 - Intervenção%' THEN 1 ELSE 0 END) as farol_vermelho,
                    SUM(CASE WHEN farol_criticidade LIKE '%2 - Saneamento%' THEN 1 ELSE 0 END) as farol_laranja,
                    SUM(CASE WHEN farol_criticidade LIKE '%3 - Monitoramento%' THEN 1 ELSE 0 END) as farol_amarelo,
                    SUM(CASE WHEN farol_criticidade LIKE '%4 - Fluxo%' THEN 1 ELSE 0 END) as farol_verde
                FROM processos_sei
            """)
            dados = cur.fetchone()
        conn.close()
        return jsonify({"status": "sucesso", "origem": "MariaDB (Base Viva)", "metricas": dados})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
'''
        idx_main = conteudo_main.rfind("if __name__")
        if idx_main != -1:
            novo_main = conteudo_main[:idx_main] + bloco_api_procs + "\n\n" + conteudo_main[idx_main:]
        else:
            novo_main = conteudo_main + bloco_api_procs

        with open(caminho_main, "w", encoding="utf-8") as f:
            f.write(novo_main)
        print("3. Rota /api/v1/processos/estatisticas registrada no main.py com sucesso!")
    else:
        print("3. Rota /api/v1/processos/estatisticas já existente no main.py.")

cur.close()
conn.close()
print("Migração concluída com sucesso!")
