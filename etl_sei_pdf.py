# -*- coding: utf-8 -*-
import pdfplumber
import re
import json
import os
import pymysql
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "regras_governanca_sei.json")

def carregar_regras():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def calcular_faixa_aging(dias, cfg):
    try: num = int(dias)
    except: return "Normal"
    faixas = cfg.get("faixas_aging", {"normal_max": 30, "atencao_max": 90, "alerta_max": 180})
    if num < 0: return "Prazo Vencido / Anomalia"
    if num <= faixas.get("normal_max", 30): return "Normal"
    if num <= faixas.get("atencao_max", 90): return "Atenção"
    if num <= faixas.get("alerta_max", 180): return "Alerta"
    return "Crítico / Gargalo"

def verificar_porem(texto, dias, cfg):
    t = str(texto or "").upper()
    try: d = int(dias)
    except: d = 0
    gatilhos = cfg.get("porem_gatilhos", {})
    prazos = cfg.get("porem_prazos", {"tolerancia_regular_max": 30, "reiteracao_obrigatoria_max": 60})

    detectado, motivo, tag_base = False, "", ""
    if any(k in t for k in gatilhos.get("eleitoral", [])):
        detectado, motivo, tag_base = True, "Período Eleitoral (Vedações Legais)", "Gargalo Externo: Período Eleitoral"
    elif any(k in t for k in gatilhos.get("orgaos_externos", [])):
        detectado, motivo, tag_base = True, "Espera por Parecer / Órgão Externo (CJ/PGE/TCE)", "Gargalo Externo: Parecer Externo"
    elif any(k in t for k in gatilhos.get("contingenciamento", [])):
        detectado, motivo, tag_base = True, "Contingenciamento Orçamentário / Financeiro", "Gargalo Externo: Contingenciamento"
    elif any(k in t for k in gatilhos.get("judicial", [])):
        detectado, motivo, tag_base = True, "Suspensão Judicial / Liminar / Impugnação", "Gargalo Externo: Suspensão Judicial"

    if not detectado:
        return {"is_suspenso": False, "motivo": "", "status_farol": "", "tag": ""}

    if d <= prazos.get("tolerancia_regular_max", 30):
        return {"is_suspenso": True, "motivo": motivo, "status_farol": "■■ Suspenso Legalmente", "tag": f"{tag_base} [Tolerância Regular]"}
    elif d <= prazos.get("reiteracao_obrigatoria_max", 60):
        return {"is_suspenso": True, "motivo": motivo, "status_farol": "■ Suspenso (Reiteração Necessária)", "tag": f"{tag_base} [Reiteração Obrigatória > 30d]"}
    else:
        return {"is_suspenso": True, "motivo": motivo, "status_farol": "■ 2 - Saneamento Prioritário", "tag": f"{tag_base} [Alerta: Limite Jurídico Excedido > 60d]"}

def classificar_bucket_eixo(tipo, espec, obs):
    txt = (str(tipo or "") + " " + str(espec or "") + " " + str(obs or "")).upper()
    if any(k in txt for k in ["LICITAÇÃO", "PREGÃO", "CONTRATAÇÃO", "AQUISIÇÃO", "TERMO DE REFERÊNCIA", "TR ", "ETP", "DFD", "ESTUDO TÉCNICO", "EDITAL", "PROCESSO DE CONTRATAÇÃO"]):
        eixo = "Esteira de Contratação"
        if any(k in txt for k in ["ADITIVO", "PRORROGAÇÃO", "REAJUSTE", "APOSTILAMENTO"]):
            bucket = "A-015. Prorrogações, Aditivos e Reajustes Contratuais"
        elif any(k in txt for k in ["PESQUISA DE PREÇO", "VANTAJOSIDADE", "COTAÇÃO"]):
            bucket = "A-013. Pesquisa de Preços e Análise de Vantajosidade"
        elif any(k in txt for k in ["TERMO DE REFERÊNCIA", "TR ", "CATÁLOGO", "UST", "PONTOS DE FUNÇÃO"]):
            bucket = "A-012. Elaboração de Termo de Referência e Catálogo"
        elif any(k in txt for k in ["PGE", "CONSULTORIA JURÍDICA", "COTA DA CJ"]):
            bucket = "A-014. Acompanhamento Jurídico e Pareceres PGE"
        else:
            bucket = "A-011. Elaboração de DFD, ETP e Matriz de Riscos"
        return eixo, bucket

    if any(k in txt for k in ["NUVEM", "CLOUD", "FINOPS", "SWITCH", "HIPERCONVERGÊNCIA", "DATACENTER", "CPD"]):
        return "Portfólio Estratégico", "A-017. Modernização de Infraestrutura e Nuvem"
    if any(k in txt for k in ["SISTEMA", "OUTORGA", "COBRANÇA", "DATA LAKE", "SIGRH", "API", "DESENVOLVIMENTO"]):
        return "Portfólio Estratégico", "A-018. Desenvolvimento de Sistemas e Data Lakehouse"
    if any(k in txt for k in ["PDTIC", "GOVERNANÇA", "PLANEJAMENTO"]):
        return "Portfólio Estratégico", "A-016. Governança de TIC, Revisão PDTIC e Inovação"

    eixo = "Rotina Operacional"
    if any(k in txt for k in ["PRODESP", "HOSTING", "DATA CENTER PRODESP", "ATESTADO DE REALIZAÇÃO"]):
        bucket = "A-001. Atestes e Medições Mensais PRODESP"
    elif any(k in txt for k in ["TELEFONICA", "CLARO", "VIVO", "FATURA", "CONCESSIONÁRIA", "ENERGIA"]):
        bucket = "A-002. Faturas e Pagamentos de Concessionárias / TI"
    elif any(k in txt for k in ["OUTSOURCING", "DAAS", "DESKTOP", "NOTEBOOK", "IMPRESSORA", "CESSÃO"]):
        bucket = "A-003. Fiscalização Técnica e IMR Outsourcing / DaaS"
    elif any(k in txt for k in ["LICENÇA", "LICENCIAMENTO", "MICROSOFT", "GOOGLE WORKSPACE", "AUTOCAD", "ARCGIS"]):
        bucket = "A-004. Gestão e Suporte de Licenciamento de Software"
    elif any(k in txt for k in ["LINK", "WAN", "SD-WAN", "INTERNET", "NOC", "INTRAGOV"]):
        bucket = "A-005. Administração de Links WAN, SD-WAN e Redes"
    elif any(k in txt for k in ["NO-BREAK", "CPD", "RACK", "CLIMATIZAÇÃO", "CABEAMENTO"]):
        bucket = "A-006. Manutenção de Infraestrutura Física e CPD"
    elif any(k in txt for k in ["BACKUP", "RESTORE", "FITAS", "WORM"]):
        bucket = "A-007. Gestão de Backup Corporativo e Políticas Restore"
    elif any(k in txt for k in ["SEGURANÇA", "SOC", "VULNERABILIDADE", "INCIDENTE", "CERTIFICADO DIGITAL", "ANTIVÍRUS", "FIREWALL"]):
        bucket = "A-008. Segurança da Informação, Incidentes e SOC"
    elif any(k in txt for k in ["LEGADO", "BANCO DE DADOS", "ORACLE", "POSTGRES"]):
        bucket = "A-009. Sustentação de Aplicações Legadas e Bancos"
    else:
        bucket = "A-010. Atendimento a Solicitações Internas e Suporte"

    return eixo, bucket

def processar_arquivos_pdf(caminhos_pdf):
    cfg = carregar_regras()
    processos = []

    for fpath in caminhos_pdf:
        if not os.path.exists(fpath): continue
        with pdfplumber.open(fpath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        row_clean = [c.replace('\n', ' ').strip() if c else '' for c in row]
                        row_str = " ".join(row_clean)
                        m_proc = re.search(r'(\d{3}\.\s*\d{8}/\d{4}-\s*\d{2})', row_str)
                        if not m_proc: continue

                        num_proc = re.sub(r'\s+', '', m_proc.group(1))
                        prefixo = num_proc.split('.')[0] if '.' in num_proc else '137'

                        anotacao = ""
                        for cell in row_clean:
                            m_anot = re.search(r'\b100\d{5,7}\b', cell)
                            if m_anot: anotacao = m_anot.group(0); break

                        tipo = row_clean[5] if len(row_clean) > 5 and len(row_clean[5]) > 5 else "Processo Administrativo"
                        espec = row_clean[6] if len(row_clean) > 6 and len(row_clean[6]) > 3 else "Demanda TIC"
                        interessados = row_clean[8] if len(row_clean) > 8 else ""
                        obs = row_clean[9] if len(row_clean) > 9 else ""

                        dias = 0
                        for cell in row_clean:
                            if cell.isdigit() and int(cell) < 2500:
                                dias = int(cell)

                        marcadores_raw = row_clean[14] if len(row_clean) > 14 else ""

                        resp = ""
                        for analista in cfg.get("analistas_conhecidos", []):
                            if analista.lower() in row_str.lower():
                                resp = analista
                                break

                        faixa_aging = calcular_faixa_aging(dias, cfg)
                        imp = verificar_porem(row_str, dias, cfg)
                        eixo, bucket = classificar_bucket_eixo(tipo, espec, obs)

                        if imp["is_suspenso"]:
                            status_op = imp["status_farol"]
                        elif eixo == "Esteira de Contratação":
                            status_op = "■ Elaboração de ETP e Riscos" if "ETP" in espec.upper() else ("■ Elaboração de TR/Projeto Básico" if "TR" in espec.upper() else "■ Formalização da Demanda")
                        elif "CONTRATO" in row_str.upper():
                            status_op = "✍■ Contrato Formalizado"
                        else:
                            status_op = "■ Em progresso" if dias < 60 else "■■ Em espera"

                        risco = "■ Alto" if (dias > 180 or "URGENTE" in row_str.upper() or "INDENIZA" in row_str.upper()) else ("■ Médio" if dias > 90 else "■ Baixo")
                        if imp["is_suspenso"]:
                            farol = imp["status_farol"]
                        elif eixo == "Rotina Operacional":
                            farol = "■ Rotina Padrão"
                        elif risco == "■ Alto":
                            farol = "■ 1 - Intervenção Imediata" if dias > 180 else "■ 2 - Saneamento Prioritário"
                        elif risco == "■ Médio":
                            farol = "■ 3 - Monitoramento Ativo"
                        else:
                            farol = "■ 4 - Fluxo Normal"

                        sinalizado = "■ SIM" if "SINALIZADO" in row_str.upper() else "NÃO"
                        hoje_str = datetime.now().strftime("%d/%m/%Y")

                        processos.append({
                            "ID_Processo": num_proc,
                            "Prefixo_Orgao": prefixo,
                            "Anotacao_Cod": anotacao,
                            "Tipo_Processo": tipo,
                            "Especificacao": espec,
                            "Interessados": interessados,
                            "Observacao_Texto": obs,
                            "Dias_Ultima_Mov": dias,
                            "Faixa_Aging": faixa_aging,
                            "Marcadores_Institucionais": marcadores_raw,
                            "Responsavel_Tecnico": resp,
                            "Eixo_Gestao": eixo,
                            "Bucket_OpenProject": bucket,
                            "Status_OpenProject": status_op,
                            "Classificacao_Risco": risco,
                            "Farol_Criticidade": farol,
                            "Sinalizado_Diretoria": sinalizado,
                            "Data_Carga_ETL": hoje_str
                        })

    dedup = {p["ID_Processo"]: p for p in processos}
    return list(dedup.values())

def gravar_no_mariadb(processos):
    conn = None
    for pwd in ['', 'root', 'glpi', 'cockpit', 'mariadb']:
        try:
            conn = pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password=pwd,
                database='glpidb', cursorclass=pymysql.cursors.DictCursor
            )
            break
        except: pass

    if not conn:
        raise Exception("Não foi possível conectar ao MariaDB glpidb na porta :3306.")

    total_novos = 0
    total_atualizados = 0

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS processos_sei (
            ID_Processo VARCHAR(50) PRIMARY KEY,
            Prefixo_Orgao VARCHAR(10),
            Anotacao_Cod VARCHAR(50),
            Tipo_Processo VARCHAR(255),
            Especificacao TEXT,
            Interessados TEXT,
            Observacao_Texto TEXT,
            Dias_Ultima_Mov INT,
            Faixa_Aging VARCHAR(50),
            Marcadores_Institucionais TEXT,
            Responsavel_Tecnico VARCHAR(150),
            Eixo_Gestao VARCHAR(100),
            Bucket_OpenProject VARCHAR(150),
            Status_OpenProject VARCHAR(100),
            Classificacao_Risco VARCHAR(50),
            Farol_Criticidade VARCHAR(50),
            Sinalizado_Diretoria VARCHAR(20),
            Data_Carga_ETL VARCHAR(30)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS historico_cargas_sei (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario VARCHAR(100),
            total_processos INT,
            arquivos_origem TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        for p in processos:
            cur.execute("SELECT ID_Processo FROM processos_sei WHERE ID_Processo = %s", (p["ID_Processo"],))
            existe = cur.fetchone()
            if existe: total_atualizados += 1
            else: total_novos += 1

            sql = """
            INSERT INTO processos_sei (
                ID_Processo, Prefixo_Orgao, Anotacao_Cod, Tipo_Processo, Especificacao,
                Interessados, Observacao_Texto, Dias_Ultima_Mov, Faixa_Aging, Marcadores_Institucionais,
                Responsavel_Tecnico, Eixo_Gestao, Bucket_OpenProject, Status_OpenProject, Classificacao_Risco,
                Farol_Criticidade, Sinalizado_Diretoria, Data_Carga_ETL
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Anotacao_Cod=VALUES(Anotacao_Cod), Tipo_Processo=VALUES(Tipo_Processo), Especificacao=VALUES(Especificacao),
                Interessados=VALUES(Interessados), Observacao_Texto=VALUES(Observacao_Texto), Dias_Ultima_Mov=VALUES(Dias_Ultima_Mov),
                Faixa_Aging=VALUES(Faixa_Aging), Marcadores_Institucionais=VALUES(Marcadores_Institucionais),
                Responsavel_Tecnico=VALUES(Responsavel_Tecnico), Eixo_Gestao=VALUES(Eixo_Gestao),
                Bucket_OpenProject=VALUES(Bucket_OpenProject), Status_OpenProject=VALUES(Status_OpenProject),
                Classificacao_Risco=VALUES(Classificacao_Risco), Farol_Criticidade=VALUES(Farol_Criticidade),
                Sinalizado_Diretoria=VALUES(Sinalizado_Diretoria), Data_Carga_ETL=VALUES(Data_Carga_ETL);
            """
            cur.execute(sql, (
                p["ID_Processo"], p["Prefixo_Orgao"], p["Anotacao_Cod"], p["Tipo_Processo"], p["Especificacao"],
                p["Interessados"], p["Observacao_Texto"], p["Dias_Ultima_Mov"], p["Faixa_Aging"], p["Marcadores_Institucionais"],
                p["Responsavel_Tecnico"], p["Eixo_Gestao"], p["Bucket_OpenProject"], p["Status_OpenProject"],
                p["Classificacao_Risco"], p["Farol_Criticidade"], p["Sinalizado_Diretoria"], p["Data_Carga_ETL"]
            ))

        cur.execute("INSERT INTO historico_cargas_sei (usuario, total_processos, arquivos_origem) VALUES (%s, %s, %s)",
                    ('Super-Admin (Luiz Seixeiro)', len(processos), 'Upload PDF Oficial'))
        conn.commit()
        conn.close()

    return total_novos, total_atualizados
