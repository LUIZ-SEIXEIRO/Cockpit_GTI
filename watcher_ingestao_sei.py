# -*- coding: utf-8 -*-
import os, sys, time, shutil, re
from datetime import datetime

BASE_DIR = os.path.join(os.getcwd(), "ingestao_sei")
DIR_NOVOS = os.path.join(BASE_DIR, "novos_pdfs")
DIR_PROCESSADOS = os.path.join(BASE_DIR, "processados")
DIR_ERROS = os.path.join(BASE_DIR, "erros")

for d in [DIR_NOVOS, DIR_PROCESSADOS, DIR_ERROS]:
    os.makedirs(d, exist_ok=True)

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

def processar_pdf(caminho_pdf):
    import pdfplumber
    processos = []
    with pdfplumber.open(caminho_pdf) as pdf:
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
                    
                    is_suspenso = any(k in row_str.upper() for k in ["AGUARDANDO PGE", "CONSULTORIA JURÍDICA", "AGUARDANDO CJ", "TCE", "CONTINGENCIAMENTO", "JUDICIAL"])
                    if is_suspenso:
                        status_op = "⏸️ Suspenso Legalmente" if dias <= 30 else ("🟡 Suspenso (Reiteração Necessária)" if dias <= 60 else "🟠 2 - Saneamento Prioritário")
                        farol = status_op
                    else:
                        status_op = "🚀 Em progresso" if dias < 60 else "⏸️ Em espera"
                        farol = "🔴 1 - Intervenção Imediata" if dias > 180 else ("🟡 3 - Monitoramento Ativo" if dias > 90 else "🟢 4 - Fluxo Normal")

                    processos.append({
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
    return processos

def gravar_no_mariadb(processos):
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
    for p in processos:
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
    conn.close()

def ciclo_monitoramento():
    print("=" * 70)
    print(" 📡 WATCHDOG MOTOR #6 SEI ONLINE — MONITORANDO PASTA...")
    print(f" Pasta de Entrada: {DIR_NOVOS}")
    print(" Pressione Ctrl+C para pausar.")
    print("=" * 70)

    while True:
        try:
            arquivos = [f for f in os.listdir(DIR_NOVOS) if f.lower().endswith(".pdf")]
            for arq in arquivos:
                caminho_completo = os.path.join(DIR_NOVOS, arq)
                
                # Aguardar estabilização do tamanho do arquivo (evita ler download incompleto)
                tamanho_anterior = -1
                while True:
                    tamanho_atual = os.path.getsize(caminho_completo)
                    if tamanho_atual == tamanho_anterior and tamanho_atual > 0:
                        break
                    tamanho_anterior = tamanho_atual
                    time.sleep(1)

                print(f"\n[NOVO ARQUIVO DETECTADO]: {arq} ({tamanho_atual / 1024:.1f} KB)")
                try:
                    procs = processar_pdf(caminho_completo)
                    print(f"[*] Processamento ETL concluído: {len(procs)} processos extraídos.")
                    gravar_no_mariadb(procs)
                    print(f"[OK] {len(procs)} registros sincronizados com sucesso no MariaDB (tabela processos_sei)!")

                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    novo_nome = f"{ts}_{arq}"
                    shutil.move(caminho_completo, os.path.join(DIR_PROCESSADOS, novo_nome))
                    print(f"[ARQUIVADO]: Movido para processados/{novo_nome}")
                except Exception as ex:
                    print(f"[ERRO NO PROCESSAMENTO]: {ex}")
                    shutil.move(caminho_completo, os.path.join(DIR_ERROS, arq))

            time.sleep(3)
        except KeyboardInterrupt:
            print("\n[!] Watchdog encerrado pelo usuário.")
            break
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    ciclo_monitoramento()
