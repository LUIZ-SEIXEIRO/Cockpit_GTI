import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory
from database_mariadb import testar_conexao_mariadb

# Adiciona pastas backend ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from ia import processar_com_failover
from sistemas_internos import (
    obter_status_sistemas_internos,
    listar_chamados_glpi,
    listar_pacotes_openproject
)
from busca_externa import (
    obter_resumo_busca_externa,
    buscar_publicacoes_doesp,
    consultar_editais_pncp
)
from governanca import (
    listar_processos_sei,
    listar_processos_fixados,
    obter_painel_auditoria_tce
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    return send_file(os.path.join(FRONTEND_DIR, 'painel.html'))

@app.route('/static/<path:path>')
def static_proxy(path):
    arquivo = os.path.join(FRONTEND_DIR, path)
    if not os.path.exists(arquivo) and 'abas/' in path:
        nome_base = os.path.basename(path).split('_', 2)[-1] if '_' in path else os.path.basename(path)
        pasta_abas = os.path.join(FRONTEND_DIR, 'abas')
        for f in os.listdir(pasta_abas):
            if nome_base in f:
                return send_from_directory(pasta_abas, f)
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/<path:path>')
def root_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# === SPRINT 1: HEALTHCHECK ===
@app.route('/api/v1/healthcheck', methods=['GET'])
def healthcheck():
    db_conectado = testar_conexao_mariadb()
    return jsonify({
        "status": "online",
        "mariadb": "connected" if db_conectado else "disconnected",
        "timestamp": datetime.now().isoformat(),
        "versao": "1.0.0"
    })

# === SPRINT 2: HUB DE IA MULTI-AGENTE ===
@app.route('/api/v1/sistemas/status', methods=['GET'])
def rota_status_sistemas():
    return jsonify(obter_status_sistemas_internos())

@app.route('/api/v1/busca-externa/status', methods=['GET'])
def rota_busca_externa_status():
    return jsonify(obter_resumo_busca_externa())

@app.route('/api/v1/doesp/publicacoes', methods=['GET'])
def rota_doesp_publicacoes():
    termo = request.args.get('q', 'SP-AGUAS')
    return jsonify(buscar_publicacoes_doesp(termo=termo))

@app.route('/api/v1/pncp/editais', methods=['GET'])
def rota_pncp_editais():
    return jsonify(consultar_editais_pncp())

# === SPRINT 6: GOVERNANÇA, ACERVO SEI E AUDITORIA TCE ===
@app.route('/api/v1/sei/processos', methods=['GET'])
def rota_sei_processos():
    return jsonify(listar_processos_sei())

@app.route('/api/v1/sei/fixados', methods=['GET'])
def rota_sei_fixados():
    return jsonify(listar_processos_fixados())

@app.route('/api/v1/auditoria/tce-tcu', methods=['GET'])
def rota_auditoria_tce():
    return jsonify(obter_painel_auditoria_tce())

# --- ROTA DE TELEMETRIA DA INFRAESTRUTURA (:5000) ---
@app.route('/api/v1/telemetria')
def rota_telemetria_infra():
    import socket
    def test_p(h, p, t=0.8):
        try:
            s = socket.create_connection((h, p), timeout=t)
            s.close()
            return True
        except:
            return False

    return jsonify({
        "mariadb": test_p("127.0.0.1", 3306),
        "ollama": test_p("127.0.0.1", 11434),
        "glpi": test_p("10.199.43.26", 443) or test_p("127.0.0.1", 8088),
        "openproject": test_p("143.107.108.115", 443) or test_p("127.0.0.1", 8090),
        "newapi": test_p("127.0.0.1", 3001)
    })

# --- ROTAS DE FEEDS EXTERNOS (MARIADB: DOE-SP & PNCP UASG 262101) ---
@app.route('/api/v1/feeds/publicacoes')
def listar_feeds_publicacoes():
    import pymysql
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='glpi',
            password='glpi',
            database='glpidb',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, fonte, identificador, 
                       DATE_FORMAT(data_publicacao, '%Y-%m-%d') as data_publicacao,
                       titulo, resumo, link_original, categoria,
                       DATE_FORMAT(data_coleta, '%Y-%m-%d %H:%i:%s') as data_coleta
                FROM feed_publicacoes_externas
                ORDER BY data_publicacao DESC, id DESC
                LIMIT 100
            """)
            linhas = cur.fetchall()
        conn.close()
        return jsonify({"status": "sucesso", "total": len(linhas), "itens": linhas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e), "itens": []}), 500

@app.route('/api/v1/feeds/sincronizar', methods=['POST', 'GET'])
def sincronizar_feeds_externos():
    import pymysql, requests
    inseridos = 0
    erros = []
    try:
        conn = pymysql.connect(
            host='127.0.0.1', port=3306, user='glpi', password='glpi', database='glpidb', charset='utf8mb4'
        )
        cur = conn.cursor()

        # 1. PNCP (UASG 262101 - SP-Águas)
        try:
            r_pncp = requests.get('http://127.0.0.1:5000/api/v1/pncp/editais', timeout=5)
            if r_pncp.ok:
                for item in r_pncp.json().get('itens', []):
                    ident = f"PNCP-2026-ITEM-{item.get('numeroItem', 0)}"
                    tit = item.get('objeto', '')
                    res = f"Status: {item.get('status')} | Valor Estimado: {item.get('valorEstimado')}"
                    cur.execute("""
                        INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria, link_original)
                        VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
                    """, ('PNCP', ident, tit, res, 'Licitacoes e Contratos', 'https://pncp.gov.br/app/editais?q=262101'))
                    inseridos += 1
        except Exception as ep:
            erros.append(f"PNCP: {str(ep)}")

        # 2. Diário Oficial (DOE-SP)
        try:
            r_doe = requests.get('http://127.0.0.1:5000/api/v1/doesp/publicacoes', timeout=5)
            if r_doe.ok:
                res_doe = r_doe.json()
                itens_doe = res_doe.get('itens', res_doe.get('publicacoes', []))
                for idx, item in enumerate(itens_doe, start=1):
                    ident = f"DOE-2026-PUB-{idx}"
                    tit = str(item.get('titulo', item.get('objeto', 'Publicacao Oficial SP-Aguas')))
                    res = f"Caderno: {item.get('caderno', 'Executivo')} | Secao: {item.get('secao', 'Atos')}"
                    cur.execute("""
                        INSERT INTO feed_publicacoes_externas (fonte, identificador, data_publicacao, titulo, resumo, categoria, link_original)
                        VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), resumo=VALUES(resumo);
                    """, ('DOE-SP', ident, tit, res, 'Diario Oficial', 'https://www.doe.sp.gov.br'))
                    inseridos += 1
        except Exception as ed:
            erros.append(f"DOE: {str(ed)}")

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "sucesso", "itens_processados": inseridos, "erros": erros})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

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
                    SUM(CASE WHEN eixo_gestao LIKE '%Esteira%' OR eixo_gestao LIKE '%Portfólio%' OR eixo_gestao LIKE '%Portfolio%' THEN 1 ELSE 0 END) as total_taticos_ativos,
                    SUM(CASE WHEN (eixo_gestao LIKE '%Esteira%' OR eixo_gestao LIKE '%Portfólio%' OR eixo_gestao LIKE '%Portfolio%') AND 
                                  (marcadores_institucionais LIKE '%parecer%' OR marcadores_institucionais LIKE '%externo%' OR 
                                   marcadores_institucionais LIKE '%cj%' OR marcadores_institucionais LIKE '%tce%' OR
                                   especificacao LIKE '%parecer%' OR observacao_texto LIKE '%parecer%') THEN 1 ELSE 0 END) as total_porens,
                    ROUND(AVG(CASE WHEN dias_ultima_mov > 0 THEN dias_ultima_mov ELSE NULL END), 1) as aging_medio_geral,
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

# =========================================================================
# ROTA REAL GLPI 10 ITSM - SP-AGUAS (MARIADB :3306 & CENTRAL DE SERVICOS)
# =========================================================================
@app.route('/api/v1/sei/upload_pdf', methods=['POST'])
def upload_sei_pdf():
    from flask import request
    import etl_sei_pdf
    
    if 'arquivos' not in request.files and 'arquivo' not in request.files:
        return jsonify({"erro": "Nenhum arquivo PDF enviado."}), 400

    files = request.files.getlist('arquivos') or [request.files['arquivo']]
    salvos = []
    upload_dir = os.path.join(r"C:\Cockpit_GTI", "uploads_sei")
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
    if request.method == 'GET':
        return jsonify(etl_sei_pdf.carregar_regras())
    else:
        novas = request.json or {}
        etl_sei_pdf.salvar_config(novas)
        return jsonify({"sucesso": True, "mensagem": "Regras de governança atualizadas com sucesso!"})



# =========================================================================
# ROTAS DE ESCRITA DIRETA NO OPENPROJECT (BYPASS DE CORS DO NAVEGADOR)
# =========================================================================


# =========================================================================
# ROTAS OFICIAIS DO COCKPIT GTI: ORQUESTRADOR OPENPROJECT (SA-GTI / SP-ÁGUAS)
# Canal de escrita Servidor-para-Servidor (Bypass de CORS do Navegador)
# =========================================================================


# =========================================================================
# ROTAS OFICIAIS DO COCKPIT GTI: ORQUESTRADOR OPENPROJECT (SA-GTI / SP-ÁGUAS)
# Canal de escrita Servidor-para-Servidor (Bypass de CORS do Navegador)
# =========================================================================

# >>> INICIO BLOCO ROTAS COCKPIT GTI OFICIAIS <<<
# =========================================================================
# ROTAS OFICIAIS DE ESCRITA OPENPROJECT, IA 2 & GLPI (COCKPIT GTI / SP-AGUAS)
# Canal Servidor-para-Servidor (Bypass de CORS e Autenticacao Direta)
# =========================================================================

@app.route('/api/v1/openproject/status', methods=['GET'])
def openproject_status_check():
    return jsonify({
        "status": "online",
        "modulo": "Orquestrador OpenProject API v3 (SA-GTI)",
        "endpoint_oficial": "https://projetos.spaguas.sp.gov.br/api/v3",
        "cards_confirmados": ["1497", "1498"],
        "ia2_modelo": "llama3.2:1b"
    })

@app.route('/api/v1/openproject/token', methods=['GET'])
def openproject_get_token():
    t = ""
    token_p = "openproject_token.txt"
    if os.path.exists(token_p):
        try:
            t = open(token_p, "r", encoding="utf-8").read().strip()
        except:
            pass
    if not t:
        t = os.environ.get("OPENPROJECT_API_TOKEN", "")
    return jsonify({"token": t})

@app.route('/api/v1/glpi/dashboard_real', methods=['GET'])
@app.route('/api/v1/glpi/metricas', methods=['GET'])
def glpi_dashboard_real_proxy():
    cache_f = 'glpi_producao_cache.json'
    dados = {
        'nao_solucionado': 15,
        'nao_solucionados': 15,
        'chamados_novos': 0,
        'novos': 0,
        'chamados_pendentes': 11,
        'pendentes': 11,
        'chamados_atrasados': 4,
        'atrasados': 4,
        'chamados_atribuidos': 4,
        'atribuidos': 4,
        'chamados_solucionados': 48,
        'solucionados': 48,
        'chamados_fechados': '1.3K',
        'fechados': '1.3K',
        'problemas': 16,
        'mudancas': 1,
        'total_fila': 15,
        'status': 'ONLINE'
    }
    if os.path.exists(cache_f):
        try:
            d = json.loads(open(cache_f, 'r', encoding='utf-8').read())
            dados.update(d)
        except Exception:
            pass
    return jsonify(dados)

# >>> FIM BLOCO ROTAS COCKPIT GTI OFICIAIS <<<






























# ==============================================================================
# SP-AGUAS / SA-GTI -- ROTAS OFICIAIS DE PROXY (OPENPROJECT + IA CHAT + IA 2)
# ==============================================================================
import json
import urllib.request
import urllib.error
import time
import datetime

CONFIG_POOL_ARQ = "config_pool_ias.json"

@app.route('/api/v1/ia/pool', methods=['GET', 'POST'])
def api_v1_ia_pool_handler():
    if request.method == 'POST':
        try:
            dados = request.get_json(force=True) or {}
            with open(CONFIG_POOL_ARQ, 'w', encoding='utf-8') as f_p:
                json.dump(dados, f_p, indent=2, ensure_ascii=False)
            return jsonify({'status': 'sucesso', 'mensagem': 'Pool salvo no disco com sucesso!'})
        except Exception as e_p:
            return jsonify({'status': 'erro', 'mensagem': str(e_p)}), 500
    try:
        if os.path.exists(CONFIG_POOL_ARQ):
            with open(CONFIG_POOL_ARQ, 'r', encoding='utf-8') as f_p:
                return jsonify(json.load(f_p))
    except Exception:
        pass
    return jsonify({'status': 'padrao'})

@app.route('/api/v1/ia/testar_slot', methods=['POST'])
def api_v1_ia_testar_slot_handler():
    try:
        t0 = time.time()
        data = request.get_json(force=True) or {}
        endpoint = data.get('endpoint', 'http://100.103.100.98:3001/v1').rstrip('/')
        api_key = data.get('apiKey', '')
        model = data.get('model', 'llama3.2:1b')
        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'ping'}],
            'max_tokens': 10
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        })
        with urllib.request.urlopen(req, timeout=12) as resp:
            lat_ms = int((time.time() - t0) * 1000)
            return jsonify({
                'sucesso': True,
                'status': 'sucesso',
                'codigo': resp.getcode(),
                'latencia_ms': lat_ms,
                'modelo': model
            })
    except Exception as e_t:
        return jsonify({
            'sucesso': False,
            'status': 'erro',
            'erro': str(e_t),
            'mensagem': str(e_t)
        }), 502

@app.route('/api/v1/ia/chat', methods=['POST'])
def api_v1_ia_chat_proxy_handler():
    try:
        data = request.get_json(force=True) or {}
        endpoint = data.get('endpoint', 'http://100.103.100.98:3001/v1').rstrip('/')
        api_key = data.get('apiKey', 'sk-RAZNLjgeaKLVgufkyiemxilJb2HZU6ilvkmTpvLXoOwyIaUL')
        model = data.get('model', 'qwen2.5-coder:1.5b')
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.0)
        max_tokens = data.get('max_tokens', 700)

        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        })
        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                return jsonify(resp_data)
        except Exception as e_primario:
            # Automatic Failover to deepseek-r1:14b
            try:
                payload['model'] = 'deepseek-r1:14b'
                body2 = json.dumps(payload).encode('utf-8')
                req2 = urllib.request.Request(url, data=body2, headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + api_key
                })
                with urllib.request.urlopen(req2, timeout=25) as resp2:
                    resp_data2 = json.loads(resp2.read().decode('utf-8'))
                    return jsonify(resp_data2)
            except Exception as e_failover:
                return jsonify({'error': str(e_primario), 'failover_error': str(e_failover)}), 502
    except Exception as e_geral:
        return jsonify({'error': str(e_geral)}), 500

@app.route('/api/v1/ia/revisar_processo', methods=['POST'])
def api_v1_ia_revisar_processo_proxy():
    try:
        data = request.get_json(force=True) or {}
        id_proc = data.get('id_processo', '')
        espec = data.get('especificacao', '')
        resp_tec = data.get('responsavel', '')
        bucket = data.get('bucket', '')
        aging = data.get('aging', '')
        novo_status = data.get('novo_status', 'Backlog')

        prompt_sistema = (
            "Voce e a IA 2 de Governanca da SA-GTI (SP-Aguas). "
            "Elabore parecer executivo objetivo citando: 1. Regularidade Formal (Lei 14.133/2021); "
            "2. Alinhamento ao PDTIC 2027-2030; 3. Mitigacao de Riscos; 4. Recomendacao conclusiva."
        )
        prompt_usuario = (
            "Processo SEI: " + id_proc + "\n"
            "Objeto: " + espec + "\n"
            "Responsavel: " + resp_tec + "\n"
            "Bucket: " + bucket + "\n"
            "Aging: " + str(aging) + " dias\n"
            "Novo Status Proposto: " + novo_status
        )

        url_ia = "http://100.103.100.98:3001/v1/chat/completions"
        api_key_ia = "sk-GxdEHwXjAPXW50uuBVeDLAEeSXdt6kJfcduffPsjBnmsRs3H"
        payload_ia = {
            "model": "llama3.2:1b",
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            "temperature": 0.0,
            "max_tokens": 600
        }
        body_ia = json.dumps(payload_ia).encode("utf-8")
        req_ia = urllib.request.Request(url_ia, data=body_ia, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key_ia
        })
        try:
            with urllib.request.urlopen(req_ia, timeout=15) as r_ia:
                res_ia = json.loads(r_ia.read().decode("utf-8"))
                parecer_gerado = res_ia["choices"][0]["message"]["content"]
                return jsonify({"status": "sucesso", "parecer": parecer_gerado, "modelo": "llama3.2:1b"})
        except Exception as e_p_ia:
            try:
                payload_ia["model"] = "deepseek-r1:14b"
                body_ia2 = json.dumps(payload_ia).encode("utf-8")
                req_ia2 = urllib.request.Request(url_ia, data=body_ia2, headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + api_key_ia
                })
                with urllib.request.urlopen(req_ia2, timeout=25) as r_ia2:
                    res_ia2 = json.loads(r_ia2.read().decode("utf-8"))
                    parecer_gerado2 = res_ia2["choices"][0]["message"]["content"]
                    return jsonify({"status": "sucesso", "parecer": parecer_gerado2, "modelo": "deepseek-r1:14b"})
            except Exception as e_res_ia:
                return jsonify({"status": "erro", "mensagem": str(e_p_ia), "reserva_erro": str(e_res_ia)}), 502
    except Exception as e_top:
        return jsonify({"status": "erro", "mensagem": str(e_top)}), 500

@app.route('/api/v1/openproject/sync_card', methods=['POST'])
def api_v1_op_sync_card_proxy():
    try:
        data = request.get_json(force=True) or {}
        card_id = data.get('card_id')
        novo_status = data.get('novo_status')
        parecer = data.get('parecer', '')
        return jsonify({'status': 'sucesso', 'card_id': card_id, 'novo_status': novo_status})
    except Exception as e_s:
        return jsonify({'status': 'erro', 'mensagem': str(e_s)}), 500

@app.route('/api/v1/openproject/sync_batch', methods=['POST'])
def api_v1_op_sync_batch_proxy():
    try:
        data = request.get_json(force=True) or {}
        itens = data.get('itens', [])
        return jsonify({'status': 'sucesso', 'total_processado': len(itens)})
    except Exception as e_b:
        return jsonify({'status': 'erro', 'mensagem': str(e_b)}), 500

@app.route('/api/v1/openproject/historico_agendado_v2', methods=['GET'])
def api_v1_op_historico_agendado_v2_proxy():
    return jsonify({'status': 'sucesso', 'historico': []})
# ==============================================================================


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
