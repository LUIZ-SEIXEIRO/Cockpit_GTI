# -*- coding: utf-8 -*-
import os
import re
import shutil
import json

BASE_DIR = r"C:\Cockpit_GTI"
CONFIG_DIR = os.path.join(BASE_DIR, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)

candidate_html = [
    os.path.join(BASE_DIR, "frontend", "painel.html"),
    os.path.join(BASE_DIR, "painel.html")
]
painel_path = next((p for p in candidate_html if os.path.exists(p)), None)
if not painel_path:
    painel_path = os.path.join(BASE_DIR, "frontend", "painel.html")

main_path = os.path.join(BASE_DIR, "main.py")
etl_script_path = os.path.join(BASE_DIR, "etl_sei_pdf.py")
config_rules_path = os.path.join(CONFIG_DIR, "regras_governanca_sei.json")

print("=" * 70)
print(" IMPLANTACAO: INGESTAO SEI VIA PDF & TRANSPARENCIA METODOLOGICA (v7.1)")
print("=" * 70)

# 1. Criar arquivo de regras de governança parametrizadas (JSON)
regras_padrao = {
    "versao_regra": "7.1",
    "data_atualizacao": "29/10/2026",
    "base_normativa": "Lei 14.133/2021, Decreto Estadual 69.339/2025 e Diretriz 01/2026 SA-GTI",
    "faixas_aging": {
        "normal_max": 30,
        "atencao_max": 90,
        "alerta_max": 180
    },
    "porem_prazos": {
        "tolerancia_regular_max": 30,
        "reiteracao_obrigatoria_max": 60
    },
    "porem_gatilhos": {
        "eleitoral": ["ELEITORAL", "ELEICAO", "ELEICOES", "DEFESO ELEITORAL", "VEDACAO ELEITORAL", "LEI 9.504"],
        "orgaos_externos": ["AGUARDANDO PGE", "CONSULTORIA JURIDICA", "AGUARDANDO CJ", "COTA DA CJ", "COTA CJ", "PARECER DA CJ", "RESPOSTA DA CJ", "SUBMETIDO A CJ", "TCE", "TRIBUNAL DE CONTAS", "MANIFESTACAO EXTERNA", "AGUARDANDO DMO", "RETIDO EM ORGAO EXTERNO"],
        "contingenciamento": ["CONTINGENCIAMENTO", "CONTINGENCIADO", "BLOQUEIO ORCAMENTARIO", "RESTRICAO DE EMPENHO", "SEM DOTACAO", "CONGELAMENTO DE RECURSOS", "AGUARDANDO CREDITO"],
        "judicial": ["SUSPENSAO JUDICIAL", "DECISAO JUDICIAL", "ORDEM JUDICIAL", "LIMINAR", "MANDADO DE SEGURANCA", "IMPUGNACAO SUSPENSIVA", "SUSPENSO POR LIMINAR"]
    },
    "analistas_conhecidos": [
        "Luiz Antonio da Silva Seixeiro", "Luiz Antonio Seixeiro", "Luiz Seixeiro",
        "Marcos Tadeu Yamamoto", "Marcos Tadeu",
        "Diego Monteiro",
        "Rafael Frossard Piteri", "Rafael Piteri",
        "Reyser Hideaki Uyeky Montenegro", "Reyser Hideaki",
        "Mario Liboni",
        "Alessandro Delbue Silva", "Alessandro Delbue",
        "Rodrigo Nunes de Souza",
        "Daniel"
    ]
}

with open(config_rules_path, "w", encoding="utf-8") as f:
    json.dump(regras_padrao, f, indent=4, ensure_ascii=False)
print("[1/5] Arquivo config/regras_governanca_sei.json gravado com sucesso!")

# 2. Criar modulo etl_sei_pdf.py
codigo_etl = '''# -*- coding: utf-8 -*-
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
                        row_clean = [c.replace('\\n', ' ').strip() if c else '' for c in row]
                        row_str = " ".join(row_clean)
                        m_proc = re.search(r'(\\d{3}\\.\\s*\\d{8}/\\d{4}-\\s*\\d{2})', row_str)
                        if not m_proc: continue

                        num_proc = re.sub(r'\\s+', '', m_proc.group(1))
                        prefixo = num_proc.split('.')[0] if '.' in num_proc else '137'

                        anotacao = ""
                        for cell in row_clean:
                            m_anot = re.search(r'\\b100\\d{5,7}\\b', cell)
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
'''

with open(etl_script_path, "w", encoding="utf-8") as f:
    f.write(codigo_etl)
print("[2/5] Motor ETL em Python criado em etl_sei_pdf.py!")

# 3. Registrar rotas /api/v1/sei/upload_pdf e /api/v1/sei/regras no main.py
if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8", errors="ignore") as f:
        mcode = f.read()

    rotas_novas = '''

# =========================================================================
# ROTAS OFICIAIS SEI: UPLOAD DE PDF, ETL v7.1 E REGRAS PARAMETRIZADAS
# =========================================================================
@app.route('/api/v1/sei/upload_pdf', methods=['POST'])
def upload_sei_pdf():
    from flask import request
    import etl_sei_pdf
    from datetime import datetime
    
    if 'arquivos' not in request.files and 'arquivo' not in request.files:
        return jsonify({"erro": "Nenhum arquivo PDF enviado."}), 400

    files = request.files.getlist('arquivos') or [request.files['arquivo']]
    salvos = []
    upload_dir = os.path.join(r"C:\\Cockpit_GTI", "uploads_sei")
    os.makedirs(upload_dir, exist_ok=True)

    for f in files:
        if f.filename.lower().endswith('.pdf'):
            dest = os.path.join(upload_dir, f.filename)
            f.save(dest)
            salvos.append(dest)

    if not salvos:
        return jsonify({"erro": "Nenhum PDF válido encontrado."}), 400

    try:
        processos = etl_sei_pdf.processar_arquivos_pdf(salvos)
        novos, atualizados = etl_sei_pdf.gravar_no_mariadb(processos)
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        return jsonify({
            "sucesso": True,
            "total_processados": len(processos),
            "novos": novos,
            "atualizados": atualizados,
            "data_hora": agora,
            "mensagem": f"Carga concluída! {len(processos)} processos sincronizados no MariaDB."
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/v1/sei/regras', methods=['GET', 'POST'])
def gerenciar_regras_sei():
    import etl_sei_pdf
    from flask import request
    if request.method == 'GET':
        return jsonify(etl_sei_pdf.carregar_regras())
    else:
        novas = request.json or {}
        etl_sei_pdf.salvar_config(novas)
        return jsonify({"sucesso": True, "mensagem": "Regras de governança atualizadas com sucesso!"})
'''
    if '/api/v1/sei/upload_pdf' not in mcode:
        with open(main_path, "a", encoding="utf-8") as f:
            f.write(rotas_novas)
        print("[3/5] Rotas do SEI registradas no main.py!")
    else:
        print("[3/5] Rotas do SEI já registradas no main.py.")

# 4. Injetar componente de Ingestão e Modais de Transparência no painel.html
if painel_path:
    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    componente_upload_html = """
            <!-- CENTRAL DE INGESTÃO VIA PDF DO SEI & TRANSPARÊNCIA METODOLÓGICA (MANUAL v7.1) -->
            <div class="table-card" style="padding: 16px 20px; margin-bottom: 18px; border-radius: 8px; border-left: 6px solid #0056d2; background: linear-gradient(90deg, #ffffff 0%, #f8fafc 100%);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
                    <div>
                        <div style="font-size:14px; font-weight:800; color:#0f2d59; display:flex; align-items:center; gap:8px;">
                            <span>📥 ATUALIZAÇÃO OFICIAL DO ACERVO SEI (UPLOAD DE PDF)</span>
                            <span style="font-size:10.5px; background:#dbeafe; color:#1e40af; padding:3px 8px; border-radius:12px; font-weight:700;">Diretriz 01/2026 SA-GTI</span>
                        </div>
                        <div style="font-size:11.5px; color:#64748b; margin-top:2px;">
                            Suba o relatório "Controle de Processos" exportado diretamente do SEI-SP (suporta partes 1 e 2 simultâneas).
                        </div>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <button class="btn btn-secondary" onclick="window.abrirModalManualGovernanca()" style="font-size:11.5px; font-weight:700; padding:6px 12px; display:inline-flex; align-items:center; gap:6px;">
                            📖 Ver Manual &amp; Critérios (v7.1)
                        </button>
                        <button class="btn btn-secondary" onclick="window.abrirModalParametrosRegras()" style="font-size:11.5px; font-weight:700; padding:6px 12px; display:inline-flex; align-items:center; gap:6px;">
                            ⚙️ Parametrizar Regras &amp; Decretos
                        </button>
                    </div>
                </div>

                <!-- ÁREA DE DROP & UPLOAD -->
                <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; background:#f1f5f9; padding:12px 16px; border-radius:6px; border:1px dashed #cbd5e1;">
                    <input type="file" id="input-pdf-sei-upload" multiple accept=".pdf" style="font-size:12px; color:#1e293b; flex:1;">
                    <button class="btn btn-primary" onclick="window.dispararUploadPdfSei()" style="background:#0056d2; border-color:#0056d2; font-size:12px; font-weight:700; padding:7px 16px;">
                        ⚡ Processar PDFs &amp; Sincronizar Base MariaDB
                    </button>
                </div>
                <div id="status-upload-sei-msg" style="margin-top:8px; font-size:11.5px; font-weight:700; color:#047857; display:none;"></div>
            </div>

            <!-- MODAL: MANUAL TÉCNICO & DIRETRIZ METODOLÓGICA v7.1 -->
            <div id="modal-manual-governanca" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.7); z-index:9999; justify-content:center; align-items:center; padding:20px;">
                <div style="background:#fff; width:92%; max-width:960px; max-height:88vh; border-radius:10px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
                    <div style="background:#002d5a; color:#fff; padding:16px 22px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:800; font-size:15px;">📖 MANUAL TÉCNICO E DIRETRIZ METODOLÓGICA Nº 01/2026 (VERSÃO 7.1 OFICIAL)</div>
                        <button onclick="document.getElementById('modal-manual-governanca').style.display='none'" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
                    </div>
                    <div style="padding:20px 24px; overflow-y:auto; line-height:1.6; font-size:12.5px; color:#1e293b;">
                        <h4 style="color:#002d5a; margin-top:0;">1. Fundamentação Legal e Arquitetura do Ecossistema</h4>
                        <p>A governança integrada de TIC da SP-Águas consolida um modelo determinístico e transparente para mensurar a inércia administrativa, prevenir vulnerabilidades jurídicas e mitigar riscos em contratações públicas de TIC (atendendo à Lei Federal 14.133/2021, Decreto Estadual 69.339/2025 e Decreto 67.799/2023 - EGD-SP).</p>

                        <h4 style="color:#002d5a;">2. Critério 1: Faixas de Aging (Inércia Temporal no SEI)</h4>
                        <ul>
                            <li><strong>Normal (0 a 30 dias):</strong> Tramitação regular dentro dos prazos regimentais e de SLA.</li>
                            <li><strong>Atenção (31 a 90 dias):</strong> Latência intermediária em instrução ou validações externas.</li>
                            <li><strong>Alerta (91 a 180 dias):</strong> Estagnação que ameaça o PCA ou renovações contratuais.</li>
                            <li><strong>Crítico / Gargalo (> 180 dias):</strong> Inércia superior a 6 meses; risco iminente de prejuízo ou perda de objeto.</li>
                        </ul>

                        <h4 style="color:#002d5a;">3. Protocolo de Segurança Jurídica nos Impedimentos Externos ("Poréns")</h4>
                        <p>Processos paralisados por fatores externos fogem à governança direta da SA-GTI e são resguardados pela margem jurídica:</p>
                        <ul>
                            <li><strong>Até 30 dias de inércia externa:</strong> <em>■■ Suspenso Legalmente</em> (Tolerância regular protegida sem cobrança).</li>
                            <li><strong>De 31 a 60 dias:</strong> <em>■ Suspenso (Reiteração)</em> (Alerta de diligência técnica e emissão de Cota de Reiteração no SEI).</li>
                            <li><strong>Acima de 60 dias:</strong> <em>■ 2 - Saneamento Prioritário</em> (Transborda para pauta de liderança e reporte à Diretoria Colegiada).</li>
                        </ul>

                        <h4 style="color:#002d5a;">4. Catálogo Canônico dos 18 Buckets EAP (Coluna 13)</h4>
                        <p>Segregação obrigatória entre A-001 e A-018: Atestes PRODESP (A-001), Concessionárias/Telecom (A-002), Outsourcing DaaS (A-003), Licenças (A-004), Links WAN (A-005), CPD (A-006), Backup 3-2-1-1-0 (A-007), SOC (A-008), Bancos (A-009), Suporte (A-010), DFD/ETP (A-011), TR e Catálogo (A-012), Pesquisa de Preços (A-013), Pareceres PGE/CJ (A-014), Aditivos (A-015), Governança/PDTIC (A-016), Nuvem/Infra (A-017) e Sistemas (A-018).</p>

                        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:12px; margin-top:16px;">
                            <strong>Responsável Técnico Metodológico:</strong> Luiz Antonio da Silva Seixeiro (Assessoria de TIC / SA-GTI) • Homologado pela Diretoria Colegiada da SP-Águas.
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODAL: PARAMETRIZAÇÃO DAS REGRAS & DECRETOS -->
            <div id="modal-parametros-regras" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.7); z-index:9999; justify-content:center; align-items:center; padding:20px;">
                <div style="background:#fff; width:92%; max-width:680px; max-height:85vh; border-radius:10px; display:flex; flex-direction:column; overflow:hidden;">
                    <div style="background:#0f172a; color:#fff; padding:16px 20px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:800; font-size:14px;">⚙️ PARAMETRIZAÇÃO DAS REGRAS DE GOVERNANÇA (DIRETRIZES &amp; DECRETOS)</div>
                        <button onclick="document.getElementById('modal-parametros-regras').style.display='none'" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
                    </div>
                    <div style="padding:20px; overflow-y:auto; font-size:12px;">
                        <div style="margin-bottom:14px;">
                            <label style="font-weight:700; display:block; margin-bottom:4px;">Base Normativa Vigente:</label>
                            <input type="text" id="cfg-base-normativa" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px;">
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:14px;">
                            <div>
                                <label style="font-weight:700; display:block; margin-bottom:4px;">Aging Normal (Máx dias):</label>
                                <input type="number" id="cfg-aging-normal" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1;">
                            </div>
                            <div>
                                <label style="font-weight:700; display:block; margin-bottom:4px;">Aging Atenção (Máx dias):</label>
                                <input type="number" id="cfg-aging-atencao" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1;">
                            </div>
                            <div>
                                <label style="font-weight:700; display:block; margin-bottom:4px;">Aging Alerta (Máx dias):</label>
                                <input type="number" id="cfg-aging-alerta" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1;">
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:16px;">
                            <div>
                                <label style="font-weight:700; display:block; margin-bottom:4px;">Tolerância Porém Regular (dias):</label>
                                <input type="number" id="cfg-porem-tolerancia" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1;">
                            </div>
                            <div>
                                <label style="font-weight:700; display:block; margin-bottom:4px;">Reiteração Obrigatória (dias):</label>
                                <input type="number" id="cfg-porem-reiteracao" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1;">
                            </div>
                        </div>
                        <button class="btn btn-primary" onclick="window.salvarNovasRegrasGovernanca()" style="background:#0056d2; width:100%; padding:8px; font-weight:700;">
                            💾 Gravar Parâmetros e Atualizar Diretrizes
                        </button>
                    </div>
                </div>
            </div>
    """

    p_cons = html.find('id="view-consulta"')
    if p_cons != -1:
        p_tcard = html.find('<div class="table-card">', p_cons)
        if p_tcard != -1:
            html = html[:p_tcard] + componente_upload_html + '\n            ' + html[p_tcard:]
            print("[4/5] Interface de Ingestão e Modais inseridos no HTML!")

    js_upload_suporte = """
    window.abrirModalManualGovernanca = function() {
        document.getElementById('modal-manual-governanca').style.display = 'flex';
    };

    window.abrirModalParametrosRegras = async function() {
        try {
            var r = await fetch('/api/v1/sei/regras');
            if (r.ok) {
                var cfg = await r.json();
                document.getElementById('cfg-base-normativa').value = cfg.base_normativa || '';
                document.getElementById('cfg-aging-normal').value = (cfg.faixas_aging || {}).normal_max || 30;
                document.getElementById('cfg-aging-atencao').value = (cfg.faixas_aging || {}).atencao_max || 90;
                document.getElementById('cfg-aging-alerta').value = (cfg.faixas_aging || {}).alerta_max || 180;
                document.getElementById('cfg-porem-tolerancia').value = (cfg.porem_prazos || {}).tolerancia_regular_max || 30;
                document.getElementById('cfg-porem-reiteracao').value = (cfg.porem_prazos || {}).reiteracao_obrigatoria_max || 60;
            }
        } catch(e) {}
        document.getElementById('modal-parametros-regras').style.display = 'flex';
    };

    window.salvarNovasRegrasGovernanca = async function() {
        var payload = {
            base_normativa: document.getElementById('cfg-base-normativa').value,
            faixas_aging: {
                normal_max: parseInt(document.getElementById('cfg-aging-normal').value, 10),
                atencao_max: parseInt(document.getElementById('cfg-aging-atencao').value, 10),
                alerta_max: parseInt(document.getElementById('cfg-aging-alerta').value, 10)
            },
            porem_prazos: {
                tolerancia_regular_max: parseInt(document.getElementById('cfg-porem-tolerancia').value, 10),
                reiteracao_obrigatoria_max: parseInt(document.getElementById('cfg-porem-reiteracao').value, 10)
            }
        };
        try {
            var r = await fetch('/api/v1/sei/regras', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (r.ok) {
                alert('Regras de governança atualizadas com sucesso!');
                document.getElementById('modal-parametros-regras').style.display = 'none';
            }
        } catch(e) {
            alert('Erro ao salvar regras: ' + e);
        }
    };

    window.dispararUploadPdfSei = async function() {
        var inp = document.getElementById('input-pdf-sei-upload');
        if (!inp || !inp.files || inp.files.length === 0) {
            alert('Selecione pelo menos um arquivo PDF do SEI para processar.');
            return;
        }

        var formData = new FormData();
        for (var i = 0; i < inp.files.length; i++) {
            formData.append('arquivos', inp.files[i]);
        }

        var msgEl = document.getElementById('status-upload-sei-msg');
        if (msgEl) {
            msgEl.style.display = 'block';
            msgEl.style.color = '#0284c7';
            msgEl.innerHTML = '⏳ Processando tabelas do PDF via ETL v7.1 e sincronizando MariaDB (:3306)...';
        }

        try {
            var r = await fetch('/api/v1/sei/upload_pdf', { method: 'POST', body: formData });
            var res = await r.json();
            if (r.ok && res.sucesso) {
                if (msgEl) {
                    msgEl.style.color = '#047857';
                    msgEl.innerHTML = '✅ ' + res.mensagem + ' (' + res.total_processados + ' processos em ' + res.data_hora + ')';
                }
                var badgeTotal = document.getElementById('consulta-total-badge');
                if (badgeTotal) badgeTotal.innerText = res.total_processados + ' PROCESSOS';
                alert('✅ Base do SEI atualizada com sucesso!\n\n• Total Processados: ' + res.total_processados + '\n• Novos Inseridos: ' + res.novos + '\n• Atualizados: ' + res.atualizados);
                setTimeout(function() { window.location.reload(); }, 1500);
            } else {
                if (msgEl) {
                    msgEl.style.color = '#dc2626';
                    msgEl.innerHTML = '❌ Erro no processamento: ' + (res.erro || 'Falha ao processar PDF');
                }
            }
        } catch(e) {
            if (msgEl) {
                msgEl.style.color = '#dc2626';
                msgEl.innerHTML = '❌ Erro de comunicação: ' + e;
            }
        }
    };
    """

    p_end_script = html.rfind('</script>')
    if p_end_script != -1:
        html = html[:p_end_script] + js_upload_suporte + '\n' + html[p_end_script:]

    tmp_path = painel_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp_path, painel_path)
    print("[5/5] painel.html gravado com proteção atômica e componente de ingestão ativo!")

print("=" * 70)
print(" SUCESSO! A esteira de ingestão de PDF e transparência está pronta.")
print(" Reinicie o Flask (py main.py) e abra http://localhost:5000/#consulta")
print("=" * 70)
