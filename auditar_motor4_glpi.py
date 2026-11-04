# -*- coding: utf-8 -*-
import sys, json, time, urllib.request, re

print("=" * 70)
print(" AUDITORIA TÉCNICA DO MOTOR #4: GLPI 10 ITSM & FORMCREATOR")
print(" Instância Oficial: https://atendimento.spaguas.sp.gov.br/")
print("=" * 70)

# 1. Teste de Handshake HTTPS com o Portal de Atendimento Oficial
url_glpi = "https://atendimento.spaguas.sp.gov.br/"
print(f"[*] 1. Testando conexão HTTPS com {url_glpi}...")
try:
    t0 = time.time()
    req = urllib.request.Request(url_glpi, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        lat = round((time.time() - t0) * 1000)
        print(f"    [OK] Portal de Atendimento ONLINE! Status HTTP: {resp.status} | Latência: {lat}ms")
except Exception as e:
    print(f"    [AVISO] Conexão com portal GLPI: {e}")

# 2. Leitura dos Chamados Canônicos no Cockpit
print("\n[*] 2. Carregando chamados de ITSM e tickets operacionais...")
paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]
conteudo_html = ""
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as f:
            conteudo_html = f.read()
            break
    except:
        continue

pos = conteudo_html.find("window.CHAMADOS_ITSM_SUPORTE = [")
end = conteudo_html.find("];", pos)
chunk = conteudo_html[pos:end]
tickets = re.findall(r'\{\s*id:\s*(\d+),\s*sei:\s*["\']([^"\']+)["\'],\s*modo:\s*["\']([^"\']+)["\'],\s*macro:\s*["\']([^"\']+)["\'],\s*tipo:\s*["\']([^"\']+)["\'],\s*titulo:\s*["\']([^"\']+)["\'],\s*bucket:\s*["\']([^"\']+)["\'],\s*fila:\s*["\']([^"\']+)["\'],\s*tecnico:\s*["\']([^"\']+)["\'],\s*status:\s*["\']([^"\']+)["\'],\s*urgencia:\s*["\']([^"\']+)["\'],\s*qg:\s*["\']([^"\']+)["\'],\s*acao:\s*["\']([^"\']+)["\']', chunk)
print(f"    [OK] Acervo Canônico: {len(tickets)} chamados especializados de ITSM mapeados!")
print(f"    Amostra #1: #{tickets[0][0]} - {tickets[0][5]} (Fila: {tickets[0][7]} | Resp: {tickets[0][8]})")

# 3. Criar Tabela e Fazer Ingestão no MariaDB (glpidb:3306)
print("\n[*] 3. Atualizando banco de dados MariaDB (tabela glpi_chamados_itsm)...")
try:
    import pymysql
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4')
    with conn.cursor() as cur:
        # DDL
        cur.execute("""
            CREATE TABLE IF NOT EXISTS glpi_chamados_itsm (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_ticket INT NOT NULL UNIQUE,
                nup_sei VARCHAR(50),
                modo VARCHAR(30),
                tipo_chamado VARCHAR(50),
                titulo VARCHAR(255) NOT NULL,
                bucket_sagti VARCHAR(100),
                fila_atendimento VARCHAR(50),
                tecnico_responsavel VARCHAR(100),
                status VARCHAR(50),
                urgencia_sla VARCHAR(50),
                qualidade_qg VARCHAR(50),
                acao_recomendada TEXT,
                link_oficial VARCHAR(255),
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Ingestão em lote
        inseridos = 0
        for t in tickets:
            id_t = int(t[0])
            nup = t[1][:50]
            modo = t[2][:30]
            tipo = t[4][:50]
            tit = t[5][:255]
            bucket = t[6][:100]
            fila = t[7][:50]
            tec = t[8][:100]
            st = t[9][:50]
            urg = t[10][:50]
            qg = t[11][:50]
            acao = t[12]
            link = f"https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id={id_t}"

            cur.execute("""
                INSERT INTO glpi_chamados_itsm 
                (id_ticket, nup_sei, modo, tipo_chamado, titulo, bucket_sagti, fila_atendimento, tecnico_responsavel, status, urgencia_sla, qualidade_qg, acao_recomendada, link_oficial)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    titulo=VALUES(titulo), status=VALUES(status), tecnico_responsavel=VALUES(tecnico_responsavel),
                    fila_atendimento=VALUES(fila_atendimento), acao_recomendada=VALUES(acao_recomendada);
            """, (id_t, nup, modo, tipo, tit, bucket, fila, tec, st, urg, qg, acao, link))
            inseridos += 1

        conn.commit()
        print(f"    [OK] Ingestão concluída com sucesso: {inseridos} chamados sincronizados no MariaDB!")

        # Consulta probatória no banco
        cur.execute("SELECT COUNT(*) FROM glpi_chamados_itsm")
        total_banco = cur.fetchone()[0]
        cur.execute("SELECT fila_atendimento, COUNT(*) FROM glpi_chamados_itsm GROUP BY fila_atendimento ORDER BY COUNT(*) DESC")
        filas_banco = cur.fetchall()
        print(f"\n    [REGISTRO AUDITADO NO MARIADB]:")
        print(f"     Total no Banco: {total_banco} chamados ativos")
        for fila, qtd in filas_banco:
            print(f"     - Fila {fila}: {qtd} chamados")
    conn.close()
except Exception as e:
    print(f"    [ERRO BANCO DE DADOS]: {e}")

# 4. Atualizar o Cockpit com a URL Oficial de Atendimento
print("\n[*] 4. Sincronizando Cockpit para https://atendimento.spaguas.sp.gov.br/apirest.php...")
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as f:
            c = f.read()
        norm = c.replace("\r\n", "\n")
        norm = norm.replace("http://localhost:8088/apirest.php", "https://atendimento.spaguas.sp.gov.br/apirest.php")
        norm = norm.replace("4. 🎫 GLPI 10 ITSM & Formcreator (:8088)", "4. 🎫 GLPI 10 ITSM & Formcreator")
        final = norm.replace("\n", "\r\n") if "\r\n" in c else norm
        with open(p, "w", encoding="utf-8") as f:
            f.write(final)
        print(f"    [OK] {p} atualizado para o endpoint oficial de atendimento!")
    except Exception as e:
        pass

print("=" * 70)
print(" LAUDO DO MOTOR #4 CONCLUÍDO")
print("=" * 70)
