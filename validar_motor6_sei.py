# -*- coding: utf-8 -*-
import os, sys, re, json
from datetime import datetime

print("=" * 70)
print(" VALIDAÇÃO DO MOTOR #6: ROBÔ DE INGESTÃO SEI v7.1 (ETL DE PDFs)")
print(" Origem: Relatório Oficial de Controle de Processos SEI SP-Águas")
print("=" * 70)

# 1. Localizar arquivo PDF para teste
pdf_candidatos = [
    os.path.join(os.getcwd(), "SEI - Controle de Processos1.pdf"),
    os.path.join(os.getcwd(), "SEI - Controle de Processos.pdf"),
    os.path.join(os.getcwd(), "user_uploaded_files", "ttl=63d", "user_uploaded", "SEI - Controle de Processos1.pdf"),
    os.path.join(os.getcwd(), "frontend", "SEI - Controle de Processos1.pdf")
]

pdf_alvo = None
for p in pdf_candidatos:
    if os.path.exists(p):
        pdf_alvo = p
        break

if not pdf_alvo:
    # Se não houver PDF solto na pasta raiz, busca qualquer .pdf que contenha SEI
    for raiz, _, arqs in os.walk(os.getcwd()):
        for a in arqs:
            if a.lower().endswith(".pdf") and "sei" in a.lower():
                pdf_alvo = os.path.join(raiz, a)
                break
        if pdf_alvo: break

if not pdf_alvo:
    print("\n[!] Nenhum arquivo PDF do SEI encontrado em C:\\Cockpit_GTI para teste.")
    print("    Copie um PDF de Controle de Processos do SEI para a pasta do Cockpit e repita o teste.")
    sys.exit(0)

print(f"\n[*] 1. Arquivo PDF Identificado:")
print(f"    Arquivo: {os.path.basename(pdf_alvo)}")
print(f"    Tamanho: {os.path.getsize(pdf_alvo) / 1024:.1f} KB")

# 2. Executar o processamento ETL com as regras do Manual v7.1
print("\n[*] 2. Executando extração com pdfplumber e regras da SA-GTI...")
try:
    import pdfplumber
except ImportError:
    os.system("pip install pdfplumber")
    import pdfplumber

analistas_conhecidos = [
    "Luiz Antonio da Silva Seixeiro", "Luiz Antonio Seixeiro", "Luiz Seixeiro",
    "Marcos Tadeu Yamamoto", "Marcos Tadeu", "Diego Monteiro",
    "Rafael Frossard Piteri", "Rafael Piteri", "Reyser Hideaki Uyeky Montenegro",
    "Mario Liboni", "Alessandro Delbue Silva", "Rodrigo Nunes de Souza"
]

def calcular_aging(dias):
    try: d = int(dias)
    except: return "Normal"
    if d <= 30: return "Normal"
    if d <= 90: return "Atenção"
    if d <= 180: return "Alerta"
    return "Crítico / Gargalo"

def classificar_bucket_e_eixo(txt_full):
    t = txt_full.upper()
    if any(k in t for k in ["LICITAÇÃO", "PREGÃO", "CONTRATAÇÃO", "AQUISIÇÃO", "TERMO DE REFERÊNCIA", "TR ", "ETP", "DFD"]):
        eixo = "Esteira de Contratação"
        if any(k in t for k in ["ADITIVO", "PRORROGAÇÃO", "REAJUSTE"]): bucket = "A-015. Prorrogações, Aditivos e Reajustes Contratuais"
        elif any(k in t for k in ["PESQUISA DE PREÇO", "COTAÇÃO"]): bucket = "A-013. Pesquisa de Preços e Análise de Vantajosidade"
        elif any(k in t for k in ["PGE", "CONSULTORIA JURÍDICA", "CJ"]): bucket = "A-014. Acompanhamento Jurídico e Pareceres PGE"
        elif "TR" in t or "TERMO DE REFERÊNCIA" in t: bucket = "A-012. Elaboração de Termo de Referência e Catálogo"
        else: bucket = "A-011. Elaboração de DFD, ETP e Matriz de Riscos"
        return eixo, bucket
    if any(k in t for k in ["NUVEM", "CLOUD", "FINOPS", "SWITCH", "DATACENTER"]): return "Portfólio Estratégico", "A-017. Modernização de Infraestrutura e Nuvem"
    if any(k in t for k in ["SISTEMA", "OUTORGA", "COBRANÇA", "DATA LAKE", "SIGRH", "API"]): return "Portfólio Estratégico", "A-018. Desenvolvimento de Sistemas e Data Lakehouse"
    if any(k in t for k in ["PDTIC", "GOVERNANÇA"]): return "Portfólio Estratégico", "A-016. Governança de TIC, Revisão PDTIC e Inovação"

    eixo = "Rotina Operacional"
    if any(k in t for k in ["PRODESP", "HOSTING"]): bucket = "A-001. Atestes e Medições Mensais PRODESP"
    elif any(k in t for k in ["TELEFONICA", "CLARO", "VIVO", "FATURA"]): bucket = "A-002. Faturas e Pagamentos de Concessionárias / TI"
    elif any(k in t for k in ["OUTSOURCING", "NOTEBOOK", "IMPRESSORA"]): bucket = "A-003. Fiscalização Técnica e IMR Outsourcing / DaaS"
    elif any(k in t for k in ["LICENÇA", "MICROSOFT", "GOOGLE"]): bucket = "A-004. Gestão e Suporte de Licenciamento de Software"
    elif any(k in t for k in ["LINK", "WAN", "SD-WAN"]): bucket = "A-005. Administração de Links WAN, SD-WAN e Redes"
    elif any(k in t for k in ["BACKUP", "RESTORE"]): bucket = "A-007. Gestão de Backup Corporativo e Políticas Restore"
    elif any(k in t for k in ["SEGURANÇA", "SOC", "VULNERABILIDADE"]): bucket = "A-008. Segurança da Informação, Incidentes e SOC"
    else: bucket = "A-010. Atendimento a Solicitações Internas e Suporte"
    return eixo, bucket

processos_extraidos = []
with pdfplumber.open(pdf_alvo) as pdf:
    for page in pdf.pages:
        tabelas = page.extract_tables()
        for tab in tabelas:
            for row in tab:
                row_clean = [c.replace('\n', ' ').strip() if c else '' for c in row]
                row_str = " ".join(row_clean)
                m = re.search(r'(\d{3}\.\s*\d{8}/\d{4}-\s*\d{2})', row_str)
                if not m: continue
                
                num_proc = re.sub(r'\s+', '', m.group(1))
                prefixo = num_proc.split('.')[0] if '.' in num_proc else '137'
                
                tipo = row_clean[5] if len(row_clean) > 5 and len(row_clean[5]) > 5 else "Processo Administrativo"
                espec = row_clean[6] if len(row_clean) > 6 and len(row_clean[6]) > 3 else "Demanda TIC"
                interessados = row_clean[8] if len(row_clean) > 8 else ""
                
                dias = 0
                for cell in row_clean:
                    if cell.isdigit() and int(cell) < 2000:
                        dias = int(cell)
                        
                resp = ""
                for a in analistas_conhecidos:
                    if a.lower() in row_str.lower():
                        resp = a
                        break
                        
                eixo, bucket = classificar_bucket_e_eixo(f"{tipo} {espec} {row_str}")
                faixa_aging = calcular_aging(dias)
                
                # Regra dos Poréns (Impedimentos Externos)
                is_suspenso = any(k in row_str.upper() for k in ["AGUARDANDO PGE", "CONSULTORIA JURÍDICA", "AGUARDANDO CJ", "TCE", "CONTINGENCIAMENTO", "JUDICIAL"])
                if is_suspenso:
                    status_op = "⏸️ Suspenso Legalmente" if dias <= 30 else ("🟡 Suspenso (Reiteração Necessária)" if dias <= 60 else "🟠 2 - Saneamento Prioritário")
                    farol = status_op
                else:
                    status_op = "🚀 Em progresso" if dias < 60 else "⏸️ Em espera"
                    farol = "🔴 1 - Intervenção Imediata" if dias > 180 else ("🟡 3 - Monitoramento Ativo" if dias > 90 else "🟢 4 - Fluxo Normal")

                processos_extraidos.append({
                    "id": num_proc,
                    "prefixo": prefixo,
                    "tipo": tipo,
                    "espec": espec,
                    "interessados": interessados,
                    "dias": dias,
                    "faixa_aging": faixa_aging,
                    "responsavel": resp,
                    "eixo": eixo,
                    "bucket": bucket,
                    "status_op": status_op,
                    "farol": farol
                })

print(f"    [OK] Extração finalizada: {len(processos_extraidos)} processos estruturados!")

# 3. Atualizar no banco MariaDB (tabela processos_sei)
print("\n[*] 3. Atualizando banco de dados MariaDB (tabela processos_sei)...")
try:
    conn = None
    try:
        import pymysql
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='glpidb')
    except Exception:
        import mysql.connector
        conn = mysql.connector.connect(host='127.0.0.1', port=3306, user='root', password='', database='glpidb')
    
    cur = conn.cursor()
    cur.execute("""
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
        responsavel_tecnico VARCHAR(150),
        eixo_gestao VARCHAR(100),
        bucket_openproject VARCHAR(100),
        status_openproject VARCHAR(50),
        data_carga_etl DATE,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    hoje_sql = datetime.now().strftime("%Y-%m-%d")
    for p in processos_extraidos:
        cur.execute("""
        INSERT INTO processos_sei 
        (id_processo, prefixo_orgao, tipo_processo, especificacao, interessados, dias_ultima_mov, faixa_aging, farol_criticidade, responsavel_tecnico, eixo_gestao, bucket_openproject, status_openproject, data_carga_etl)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            tipo_processo = VALUES(tipo_processo),
            especificacao = VALUES(especificacao),
            interessados = VALUES(interessados),
            dias_ultima_mov = VALUES(dias_ultima_mov),
            faixa_aging = VALUES(faixa_aging),
            farol_criticidade = VALUES(farol_criticidade),
            responsavel_tecnico = VALUES(responsavel_tecnico),
            eixo_gestao = VALUES(eixo_gestao),
            bucket_openproject = VALUES(bucket_openproject),
            status_openproject = VALUES(status_openproject),
            data_carga_etl = VALUES(data_carga_etl);
        """, (p["id"], p["prefixo"], p["tipo"], p["espec"], p["interessados"], p["dias"], p["faixa_aging"], p["farol"], p["responsavel"], p["eixo"], p["bucket"], p["status_op"], hoje_sql))

    conn.commit()
    print("    [OK] Ingestão idempotente (UPSERT) concluída com sucesso no MariaDB!")

    cur.execute("SELECT COUNT(*), COUNT(DISTINCT responsavel_tecnico), SUM(CASE WHEN dias_ultima_mov > 180 THEN 1 ELSE 0 END) FROM processos_sei;")
    tot_banco, tot_resp, tot_crit = cur.fetchone()

    cur.execute("SELECT eixo_gestao, COUNT(*) FROM processos_sei GROUP BY eixo_gestao;")
    rows_eixos = cur.fetchall()

    print("\n    [REGISTRO AUDITADO NO MARIADB]:")
    print(f"     • Total de Processos Ativos no Banco: {tot_banco}")
    print(f"     • Processos em Faixa Crítica (> 180 dias): {tot_crit}")
    for r in rows_eixos:
        print(f"     • Eixo '{r[0]}': {r[1]} processos")

    conn.close()
except Exception as e:
    print(f"    [AVISO BANCO DE DADOS]: {e}")

# Amostra canônica do primeiro processo processado
if processos_extraidos:
    amostra = processos_extraidos[0]
    print(f"\n[*] Amostra #1 Extraída do Relatório:")
    print(f"    Processo: {amostra['id']} | Eixo: {amostra['eixo']}")
    print(f"    Objeto: {amostra['espec'][:65]}...")
    print(f"    Aging: {amostra['dias']} dias ({amostra['faixa_aging']}) | Farol: {amostra['farol']}")
    print(f"    Bucket OpenProject: {amostra['bucket']}")

print("\n" + "=" * 70)
print(" LAUDO DO MOTOR #6 CONCLUÍDO COM SUCESSO")
print("=" * 70)
