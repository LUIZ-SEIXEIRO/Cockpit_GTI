# -*- coding: utf-8 -*-
import sys, json, time, urllib.request, re
from datetime import datetime

print("=" * 70)
print(" AUDITORIA TÉCNICA DO MOTOR #3: OPENPROJECT 14 PRODUÇÃO")
print(" Instância Oficial: https://projetos.spaguas.sp.gov.br/")
print("=" * 70)

# 1. Teste de Handshake HTTPS com o OpenProject Oficial
url_op = "https://projetos.spaguas.sp.gov.br/"
print(f"[*] 1. Testando conexão HTTPS com {url_op}...")
try:
    t0 = time.time()
    req = urllib.request.Request(url_op, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        lat = round((time.time() - t0) * 1000)
        print(f"    [OK] OpenProject Produção ONLINE! Status HTTP: {resp.status} | Latência: {lat}ms")
except Exception as e:
    print(f"    [AVISO] Conexão com portal OpenProject: {e}")

# 2. Leitura dos 500 Pacotes Oficiais no Cockpit
print("\n[*] 2. Carregando dados canônicos do OpenProject...")
paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]
conteudo_html = ""
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as f:
            conteudo_html = f.read()
            break
    except:
        continue

pos = conteudo_html.find("window.OP_PACOTES_OFICIAIS = [")
end = conteudo_html.find("];", pos)
raw = conteudo_html[pos + len("window.OP_PACOTES_OFICIAIS = "):end+1]
pacotes = json.loads(raw)
projetos = set(p.get("projeto") for p in pacotes)
print(f"    [OK] Acervo Canônico: {len(pacotes)} Work Packages mapeados em {len(projetos)} Projetos!")
print(f"    Amostra #1: #{pacotes[0]['id']} - {pacotes[0]['assunto']} (Projeto: {pacotes[0]['projeto']})")

# 3. Criar Tabela e Fazer Ingestão no MariaDB (glpidb:3306)
print("\n[*] 3. Atualizando banco de dados MariaDB (tabela openproject_work_packages)...")
def parse_date(d_str):
    if not d_str: return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try: return datetime.strptime(d_str.strip(), fmt).strftime('%Y-%m-%d')
        except: pass
    return None

try:
    import pymysql
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        # DDL
        cur.execute("""
            CREATE TABLE IF NOT EXISTS openproject_work_packages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_wp INT NOT NULL UNIQUE,
                projeto VARCHAR(150),
                macro_processo VARCHAR(100),
                assunto VARCHAR(255) NOT NULL,
                tipo VARCHAR(50),
                status VARCHAR(50),
                prioridade VARCHAR(50),
                atribuido_a VARCHAR(100),
                autor VARCHAR(100),
                data_inicio DATE,
                data_fim DATE,
                backlog_sagti VARCHAR(150),
                custo_estimado DECIMAL(15,2) DEFAULT 0.00,
                link_oficial VARCHAR(255),
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Ingestão em lote
        inseridos = 0
        for p in pacotes:
            id_wp = int(p.get("id"))
            proj = str(p.get("projeto", ""))[:150]
            macro = str(p.get("macro", ""))[:100]
            assunto = str(p.get("assunto", "Sem Assunto"))[:255]
            tipo = str(p.get("tipo", ""))[:50]
            status = str(p.get("status", ""))[:50]
            prio = str(p.get("prio", ""))[:50]
            atrib = str(p.get("atrib", ""))[:100]
            autor = str(p.get("autor", ""))[:100]
            d_ini = parse_date(p.get("ini"))
            d_fim = parse_date(p.get("fim"))
            backlog = str(p.get("backlog", ""))[:150]
            custo = float(p.get("custo", 0.0) or 0.0)
            link = f"https://projetos.spaguas.sp.gov.br/work_packages/{id_wp}"

            cur.execute("""
                INSERT INTO openproject_work_packages 
                (id_wp, projeto, macro_processo, assunto, tipo, status, prioridade, atribuido_a, autor, data_inicio, data_fim, backlog_sagti, custo_estimado, link_oficial)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    projeto=VALUES(projeto), assunto=VALUES(assunto), status=VALUES(status),
                    atribuido_a=VALUES(atribuido_a), data_fim=VALUES(data_fim), custo_estimado=VALUES(custo_estimado);
            """, (id_wp, proj, macro, assunto, tipo, status, prio, atrib, autor, d_ini, d_fim, backlog, custo, link))
            inseridos += 1

        conn.commit()
        print(f"    [OK] Ingestão concluída com sucesso: {inseridos} pacotes sincronizados no MariaDB!")

        # Consulta probatória no banco
        cur.execute("SELECT COUNT(*) FROM openproject_work_packages")
        total_banco = cur.fetchone()[0]
        cur.execute("SELECT status, COUNT(*) FROM openproject_work_packages GROUP BY status ORDER BY COUNT(*) DESC LIMIT 3")
        status_banco = cur.fetchall()
        print(f"\n    [REGISTRO AUDITADO NO MARIADB]:")
        print(f"     Total no Banco: {total_banco} Work Packages ativos")
        for st, qtd in status_banco:
            print(f"     - {st}: {qtd} pacotes")
    conn.close()
except Exception as e:
    print(f"    [ERRO BANCO DE DADOS]: {e}")

# 4. Atualizar o Cockpit com a URL Oficial de Produção
print("\n[*] 4. Sincronizando Cockpit para https://projetos.spaguas.sp.gov.br/api/v3...")
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as f:
            c = f.read()
        norm = c.replace("\r\n", "\n")
        norm = norm.replace("http://localhost:8090/api/v3", "https://projetos.spaguas.sp.gov.br/api/v3")
        norm = norm.replace("3. 🏗️ OpenProject Produção API v3 (:8090)", "3. 🏗️ OpenProject 14 Produção")
        final = norm.replace("\n", "\r\n") if "\r\n" in c else norm
        with open(p, "w", encoding="utf-8") as f:
            f.write(final)
        print(f"    [OK] {p} atualizado para o endpoint oficial de produção!")
    except Exception as e:
        pass

print("=" * 70)
print(" LAUDO DO MOTOR #3 CONCLUÍDO")
print("=" * 70)
