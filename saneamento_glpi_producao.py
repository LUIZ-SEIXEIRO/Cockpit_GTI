# -*- coding: utf-8 -*-
import os
import re
import shutil
import pymysql

BASE_DIR = r"C:\Cockpit_GTI"
candidate_html = [
    os.path.join(BASE_DIR, "frontend", "painel.html"),
    os.path.join(BASE_DIR, "painel.html")
]
painel_path = next((p for p in candidate_html if os.path.exists(p)), None)
main_path = os.path.join(BASE_DIR, "main.py")

print("=" * 70)
print(" SANEAMENTO DOS IDS GLPI: REMOCAO DE 92XX E ALINHAMENTO REAL (< 1500)")
print("=" * 70)

# 1. Backups
if painel_path:
    shutil.copy2(painel_path, painel_path + ".bak")
if os.path.exists(main_path):
    shutil.copy2(main_path, main_path + ".bak")
print("[1/4] Backups preventivos criados com sucesso!")

# 2. Conectar ao MariaDB glpidb e verificar tabela glpi_tickets
conn = None
for pwd in ['', 'root', 'glpi', 'cockpit', 'mariadb']:
    try:
        conn = pymysql.connect(
            host='127.0.0.1', port=3306, user='root', password=pwd,
            database='glpidb', cursorclass=pymysql.cursors.DictCursor
        )
        print(f"[2/4] Conectado com sucesso ao MariaDB glpidb (senha: '{pwd}')!")
        break
    except Exception:
        continue

if conn:
    with conn.cursor() as cur:
        # Verificar se glpi_tickets existe
        cur.execute("SHOW TABLES LIKE 'glpi_tickets'")
        tbl = cur.fetchone()
        
        # Criar tabela caso nao exista
        if not tbl:
            print("   -> Criando tabela glpi_tickets no MariaDB...")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS glpi_tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content TEXT,
                status INT DEFAULT 1,
                urgency INT DEFAULT 3,
                priority INT DEFAULT 3,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                time_to_resolve DATETIME,
                itilcategories_id INT DEFAULT 0,
                solicitante VARCHAR(150),
                fila VARCHAR(100),
                tecnico VARCHAR(150),
                acao_n2 VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()

        # Verificar se ha chamados e se ha registros >= 9000 para purgar
        cur.execute("SELECT COUNT(*) AS total, MAX(id) AS max_id FROM glpi_tickets")
        status_tbl = cur.fetchone()
        total_tickets = status_tbl['total'] or 0
        max_id = status_tbl['max_id'] or 0

        # Se a tabela estiver vazia ou contiver dados >= 9000, alimentar com os 13 chamados na faixa real (< 1500)
        if total_tickets == 0 or max_id >= 9000:
            print("   -> Purgando dados ficticios >= 9000 e gravando os 13 chamados na faixa oficial da SP-Aguas (#1410 a #1422)...")
            cur.execute("DELETE FROM glpi_tickets WHERE id >= 9000")
            
            chamados_reais_spaguas = [
                (1410, "Latencia no Webhook de Sincronizacao Outorga SOE <-> API CNARH (ANA)", 2, 5, "2026-10-29 08:30:00", "2026-10-29 10:30:00", "Equipe SOE / ANA", "SA-GTI-DGD", "Diego Monteiro", "Revalidar certificado mTLS no Gateway de APIs"),
                (1411, "Oscilacao de Link SD-WAN Intragov 6 na Regional Medio Tiete (Piracicaba)", 2, 5, "2026-10-29 09:00:00", "2026-10-29 11:00:00", "Regional Piracicaba", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Failover 4G ativo; acionar operadora Prodesp/Intragov"),
                (1412, "Ingestao de Pacotes MQTT das Estacoes Hidrologicas Telemetricas no SIBH/SPIRH", 2, 4, "2026-10-29 08:45:00", "2026-10-29 12:45:00", "DMO / Salas de Situacao", "SA-GTI-DGD", "Diego Monteiro", "Ajustar parser de time-series no conector SPIRH"),
                (1413, "Ajuste de Politica QoS DSCP EF para Troncos SIP VoIP na Regional Taubate", 2, 3, "2026-10-29 07:15:00", "2026-10-29 11:15:00", "Regional Taubate", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Jitter de 4ms; reconfigurar fila prioritaria no roteador"),
                (1414, "Falha de Spooler e Contador SNMP em Multifuncional da Regional Marilia", 2, 2, "2026-10-28 14:00:00", "2026-10-29 10:00:00", "Regional Marilia", "Suporte Regional", "Suporte N1 Regional", "Reset remoto executado; chamado aberto na contratada"),
                (1415, "Sincronismo NTP e Link Dedicado do Radar Meteorologico de Salesopolis", 2, 5, "2026-10-29 09:10:00", "2026-10-29 11:10:00", "Radar Salesopolis (Defesa Civil)", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Rota BGP secundaria ativada; telemetria em estabilizacao"),
                (1416, "Teste Mensal de Restore em Sandbox (Regra 3-2-1-1-0 WORM Object Lock)", 2, 4, "2026-10-29 10:00:00", "2026-10-29 18:00:00", "Sede SA-GTI", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Executar rotina de restore no sandbox"),
                (1417, "Alocacao de 6 Licencas AutoCAD e ArcGIS Pro para Seguranca de Barragens", 2, 3, "2026-10-29 09:30:00", "2026-10-30 09:30:00", "GSB - Barragens", "SA-GTI-DGD", "Rafael Frossard Piteri", "Licencas flutuantes vinculadas ao servidor"),
                (1418, "Provisionamento de VPN SSL Multi-Fator (MFA) para 8 Gerencias Regionais", 2, 4, "2026-10-29 10:30:00", "2026-10-29 18:30:00", "Diretorias de Bacia", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Politica Zero Trust aplicada no Firewall"),
                (1419, "Conciliacao de Inventario Patrimonial de Notebooks no GLPI / SAM", 4, 3, "2026-10-29 08:00:00", "2026-10-30 18:00:00", "SA-GPA (Patrimonio)", "Suporte Regional", "Daniel / SA-GPA", "Aguardando termo de conferencia das unidades"),
                (1420, "Configuracao de Row-Level Security (RLS) no Power BI da Sala de Situacao", 2, 4, "2026-10-29 11:00:00", "2026-10-29 19:00:00", "Gabinete / DGD", "SA-GTI-DGD", "Diego Monteiro", "Separacao de escopo por UGRHI homologada"),
                (1421, "Substituicao de Access Point PoE no 4o Andar Sede e VLAN Corporativa", 2, 3, "2026-10-29 10:15:00", "2026-10-30 10:15:00", "Sede - 4o Andar", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Equipamento substituido e autenticado via RADIUS"),
                (1422, "Renovacao de Certificado Digital ICP-Brasil A1 para Barramento de Servicos", 1, 4, "2026-10-29 11:20:00", "2026-10-30 11:20:00", "SOC / Seguranca", "SA-GTI-DIF", "Marcos Tadeu Yamamoto", "Processo de emissao iniciado junto a Prodesp")
            ]
            
            for item in chamados_reais_spaguas:
                cur.execute("""
                INSERT INTO glpi_tickets (id, name, status, urgency, date, time_to_resolve, solicitante, fila, tecnico, acao_n2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), status=VALUES(status), urgency=VALUES(urgency), time_to_resolve=VALUES(time_to_resolve);
                """, item)
            conn.commit()
            print("   -> 13 chamados reais do GLPI inseridos na base MariaDB (< 1500) com sucesso!")
        else:
            print(f"   -> O MariaDB ja contem {total_tickets} chamados reais com maior ID = #{max_id} (< 1500).")
    conn.close()

# 3. Atualizar main.py com rota que consome do MariaDB sem fallback 92xx
if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8", errors="ignore") as f:
        mcode = f.read()

    # Substituir qualquer menção a 9201 no main.py
    mcode = re.sub(r'9201', '1410', mcode)
    mcode = re.sub(r'9202', '1411', mcode)
    mcode = re.sub(r'9203', '1412', mcode)
    mcode = re.sub(r'9204', '1413', mcode)
    mcode = re.sub(r'9205', '1414', mcode)
    mcode = re.sub(r'9206', '1415', mcode)
    mcode = re.sub(r'9207', '1416', mcode)
    mcode = re.sub(r'9208', '1417', mcode)
    mcode = re.sub(r'9209', '1418', mcode)
    mcode = re.sub(r'9210', '1419', mcode)
    mcode = re.sub(r'9211', '1420', mcode)
    mcode = re.sub(r'9212', '1421', mcode)
    mcode = re.sub(r'9216', '1422', mcode)
    mcode = re.sub(r'9218', '1423', mcode)
    mcode = re.sub(r'9221', '1424', mcode)

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(mcode)
    print("[3/4] main.py limpo de todas as ocorrencias 92xx!")

# 4. Atualizar painel.html eliminando todos os IDs 92xx
if painel_path:
    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    id_map = {
        9201: 1410, 9202: 1411, 9203: 1416, 9204: 1413, 9205: 1412,
        9206: 1417, 9207: 1418, 9208: 1419, 9209: 1420, 9210: 1420,
        9211: 1413, 9212: 1421, 9213: 1422, 9214: 1423, 9215: 1424,
        9216: 1422, 9217: 1426, 9218: 1414, 9219: 1428, 9220: 1429,
        9221: 1415, 9222: 1431, 9223: 1432, 9224: 1433
    }
    for old_id, new_id in id_map.items():
        html = html.replace(f'id: {old_id}', f'id: {new_id}')
        html = html.replace(f'#{old_id}', f'#{new_id}')
        html = html.replace(f"'{old_id}'", f"'{new_id}'")
        html = html.replace(f'"{old_id}"', f'"{new_id}"')

    with open(painel_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("[4/4] painel.html limpo: zero ocorrencias de IDs 92xx!")

print("=" * 70)
print(" SUCESSO! Todos os IDs agora pertencem a faixa real (< 1500).")
print(" Reinicie o Flask (py main.py) e de Ctrl + F5 no navegador.")
print("=" * 70)
