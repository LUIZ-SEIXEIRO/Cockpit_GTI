import pymysql
import requests

# 1. Conexao com o MariaDB
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='glpi',
    password='glpi',
    database='glpidb',
    charset='utf8mb4'
)
cur = conn.cursor()

# 2. Criar a tabela se nao existir
cur.execute('''
CREATE TABLE IF NOT EXISTS feed_publicacoes_externas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fonte VARCHAR(50) NOT NULL,
    identificador VARCHAR(100) UNIQUE,
    data_publicacao DATE,
    titulo VARCHAR(255) NOT NULL,
    resumo TEXT,
    link_original VARCHAR(500),
    categoria VARCHAR(100),
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
''')

# 3. Coletar e Persistir dados do PNCP (UASG 262101)
try:
    r_pncp = requests.get('http://localhost:5000/api/v1/pncp/editais', timeout=5)
    if r_pncp.ok:
        dados_pncp = r_pncp.json().get('itens', [])
        for item in dados_pncp:
            n_item = item.get('numeroItem', 0)
            identificador = f'PNCP-2026-ITEM-{n_item}'
            titulo = item.get('objeto', '')
            resumo = f"Status: {item.get('status')} | Valor Estimado: {item.get('valorEstimado')}"
            cur.execute('''
                INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria)
                VALUES (%s, %s, CURDATE(), %s, %s, %s)
                ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
            ''', ('PNCP', identificador, titulo, resumo, 'Licitacoes e Contratos'))
except Exception as e:
    print('Erro na captura do PNCP:', e)

# 4. Coletar e Persistir dados do DOE-SP
try:
    r_doe = requests.get('http://localhost:5000/api/v1/doesp/publicacoes', timeout=5)
    if r_doe.ok:
        res_json = r_doe.json()
        itens_doe = res_json.get('itens', res_json.get('publicacoes', []))
        for idx, item in enumerate(itens_doe, start=1):
            identificador = f'DOE-2026-PUB-{idx}'
            titulo = str(item.get('titulo', item.get('objeto', 'Publicacao Oficial SP-Aguas')))
            resumo = str(item.get('resumo', item.get('status', 'Caderno Executivo')))
            cur.execute('''
                INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria)
                VALUES (%s, %s, CURDATE(), %s, %s, %s)
                ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
            ''', ('DOE-SP', identificador, titulo, resumo, 'Diario Oficial'))
except Exception as e:
    print('Erro na captura do DOE-SP:', e)

conn.commit()

# 5. Listar os dados persistidos fisicamente no MariaDB
cur.execute('SELECT id, fonte, identificador, LEFT(titulo, 45), categoria FROM feed_publicacoes_externas;')
linhas = cur.fetchall()
print('\n=== DADOS SALVOS COM SUCESSO NO MARIADB ===')
for l in linhas:
    print(f'[{l[0]}] {l[1]} | {l[2]} | {l[3]}... | {l[4]}')

cur.close()
conn.close()
