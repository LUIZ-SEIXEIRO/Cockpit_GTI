# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from functools import wraps
import os
import sys
import json
import time
import socket
import ssl
import base64
import urllib.request
import urllib.error
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1", "cockpit.spaguas.gov.br"}
ALLOWED_ORIGINS = {
    "http://localhost:5000", "http://127.0.0.1:5000",
    "http://localhost:3000", "http://127.0.0.1:3000",
    "https://cockpit.spaguas.gov.br"
}

def validar_origem_estrita(origem):
    if not origem:
        return False
    try:
        parsed = urlparse(origem)
        return (parsed.hostname in ALLOWED_HOSTS) or (origem.rstrip("/") in ALLOWED_ORIGINS)
    except Exception:
        return False

def requer_autenticacao(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        token_esperado = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN")
        auth_header = request.headers.get("Authorization", "")
        token_fornecido = auth_header.replace("Bearer ", "").strip() if auth_header else request.headers.get("X-API-Key", "")
        
        if token_esperado:
            if token_fornecido and token_fornecido == token_esperado:
                return f(*args, **kwargs)
            return jsonify({"erro": "Acesso não autorizado: token inválido ou ausente"}), 401
            
        # Se não há token configurado, rejeita qualquer origem externa ou forjada
        origem = request.headers.get("Origin") or request.headers.get("Referer")
        if validar_origem_estrita(origem) or request.remote_addr in ("127.0.0.1", "::1"):
            return f(*args, **kwargs)
            
        return jsonify({"erro": "Acesso não autorizado: autenticação requerida"}), 401
    return decorado


# ==========================================
# SEGURANÇA E AUTENTICAÇÃO INSTITUCIONAL
# ==========================================
COCKPIT_API_TOKEN = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN") or ""
API_TOKEN = COCKPIT_API_TOKEN
OPENPROJECT_API_TOKEN = os.getenv("OPENPROJECT_API_TOKEN") or os.getenv("OPENPROJECT_API_KEY") or ""
OPENPROJECT_API_KEY = OPENPROJECT_API_TOKEN
NEWAPI_API_KEY = os.getenv("NEWAPI_API_KEY") or os.getenv("NEW_API_KEY") or ""
NEW_API_KEY = NEWAPI_API_KEY
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1")

ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1", "cockpit.spaguas.gov.br"}
ALLOWED_ORIGINS = {
    "http://localhost:5000", "http://127.0.0.1:5000",
    "http://localhost:3000", "http://127.0.0.1:3000",
    "https://cockpit.spaguas.gov.br"
}

# [Função legada de startswith expurgada]

def requer_autenticacao(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        token_esperado = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN")
        auth_header = request.headers.get("Authorization", "")
        token_fornecido = auth_header.replace("Bearer ", "").strip() if auth_header else request.headers.get("X-API-Key", "")
        
        # 1. Se houver token configurado, validação estrita do token
        if token_esperado:
            if token_fornecido and token_fornecido == token_esperado:
                return f(*args, **kwargs)
            return jsonify({"erro": "Acesso não autorizado: token inválido ou ausente"}), 401
            
        # 2. Se token_fornecido for enviado sem token no server, rejeita
        if not token_esperado and not token_fornecido:
            origem = request.headers.get("Origin") or request.headers.get("Referer")
            if validar_origem_estrita(origem) or request.remote_addr in ("127.0.0.1", "::1"):
                return f(*args, **kwargs)
                
        return jsonify({"erro": "Acesso não autorizado: autenticação requerida"}), 401
    return decorado


# -------------------------------------------------------------------------
# FUNÇÃO GLOBAL DE VERIFICAÇÃO DE PORTAS (DISPONÍVEL PARA TODAS AS ROTAS)
# -------------------------------------------------------------------------
def checar_porta(host, porta, timeout=0.8):
    try:
        s = socket.create_connection((host, porta), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False

# -------------------------------------------------------------------------
# SEGURANÇA INSTITUCIONAL & HARDENING DE REDE (DEVSECOPS / TCE-SP)
# -------------------------------------------------------------------------
ALLOWED_ORIGINS = {
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'http://100.103.100.98:5000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://100.103.100.98:3001'
}

for o in os.environ.get('ALLOWED_ORIGINS', '').split(','):
    if o.strip():
        ALLOWED_ORIGINS.add(o.strip())

COCKPIT_API_TOKEN = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN")
API_TOKEN = COCKPIT_API_TOKEN
OPENPROJECT_API_TOKEN = os.getenv("OPENPROJECT_API_TOKEN") or os.getenv("OPENPROJECT_API_KEY")
OPENPROJECT_API_KEY = OPENPROJECT_API_TOKEN
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1")

@app.after_request
def adicionar_headers_cors(response):
    origin = request.headers.get('Origin', '')
    if validar_origem_estrita(origin):
        response.headers['Access-Control-Allow-Origin'] = origin
    elif not origin and request.method == 'GET':
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5000'
    else:
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5000'

    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
    elif not origin and request.method == 'GET':
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5000'

    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-Cockpit-Token'

    # Headers OWASP
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    return response

@app.before_request
def proteger_rotas_mutaveis():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    rotas_protegidas = {
        '/api/v1/ia/pool',
        '/api/v1/ia/chat',
        '/api/v1/ia/testar_slot',
        '/api/v1/openproject/sync_card',
        '/api/v1/openproject/sync_batch'
    }

    if (request.path in rotas_protegidas and request.method in ('POST', 'PUT', 'PATCH', 'DELETE')) or request.path in ('/api/v1/ia/chat', '/api/v1/ia/testar_slot'):
        token_esperado = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN")
        
        # Se o servidor não possui token configurado no ambiente, bloqueia mutações
        if not token_esperado:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Acesso negado: API_TOKEN não configurado no servidor.'}), 401

        auth_header = request.headers.get('Authorization', '')
        token_bearer = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''
        custom_token = request.headers.get('X-Cockpit-Token', '').strip()
        token_recebido = token_bearer or custom_token

        if not token_recebido or token_recebido != token_esperado:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Acesso negado: token inválido ou ausente.'}), 401


def encontrar_arquivo_painel():
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(base, 'painel.html'),
        os.path.join(base, 'frontend', 'painel.html'),
        os.path.abspath('painel.html'),
        os.path.abspath('frontend/painel.html')
    ]
    for c in candidatos:
        if os.path.exists(c):
            return os.path.split(os.path.abspath(c))
    return None, None

@app.route('/')
@app.route('/painel')
@app.route('/frontend/painel.html')
def rota_raiz():
    d, f = encontrar_arquivo_painel()
    if d and f:
        return send_from_directory(d, f)
    return "<h2>Cockpit GTI: painel.html não encontrado</h2>", 404

@app.route('/static/<path:filename>')
@app.route('/frontend/<path:filename>')
def servir_estaticos(filename):
    base = os.path.dirname(os.path.abspath(__file__))
    pastas = [os.path.join(base, 'frontend'), os.path.abspath('frontend')]
    for p in pastas:
        if os.path.exists(os.path.join(p, filename)):
            return send_from_directory(p, filename)
    return "Arquivo não encontrado", 404

def normalizar_endpoint_ia(endpoint):
    if not endpoint:
        endpoint = 'http://127.0.0.1:3001/v1'
    endpoint = endpoint.strip().rstrip('/')
    if not endpoint.endswith('/v1'):
        endpoint += '/v1'
    return endpoint

def localizar_config_pool():
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(base, 'config_pool_ias.json'),
        os.path.join(base, 'backend', 'config_pool_ias.json'),
        os.path.abspath('config_pool_ias.json')
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return os.path.join(base, 'config_pool_ias.json')

# -------------------------------------------------------------------------
# 1. TELEMETRIA E HEALTH CHECKS INDIVIDUAIS
# -------------------------------------------------------------------------
@app.route('/api/v1/telemetria', methods=['GET'])
def rota_telemetria():
    status = {
        'mariadb': checar_porta('127.0.0.1', 3306),
        'ollama': checar_porta('127.0.0.1', 11434) or checar_porta('ollama', 11434),
        'glpi': checar_porta('10.199.43.26', 443) or checar_porta('127.0.0.1', 8088),
        'openproject': checar_porta('143.107.108.115', 443) or checar_porta('127.0.0.1', 8090),
        'newapi': checar_porta('127.0.0.1', 3001) or checar_porta('100.103.100.98', 3001) or checar_porta('new-api', 3000)
    }
    return jsonify(status), 200

@app.route('/api/v1/mariadb/status', methods=['GET'])
def mariadb_status():
    ok = checar_porta('127.0.0.1', 3306)
    return jsonify({'servico': 'mariadb', 'status': 'online' if ok else 'offline', 'ok': ok}), 200

@app.route('/api/v1/ia/status', methods=['GET'])
@app.route('/api/v1/newapi/status', methods=['GET'])
def ia_status():
    ok = checar_porta('127.0.0.1', 3001) or checar_porta('100.103.100.98', 3001) or checar_porta('new-api', 3000)
    return jsonify({'servico': 'new-api', 'status': 'online' if ok else 'offline', 'ok': ok}), 200

@app.route('/api/v1/ollama/status', methods=['GET'])
def ollama_status():
    ok = checar_porta('127.0.0.1', 11434) or checar_porta('ollama', 11434)
    return jsonify({'servico': 'ollama', 'status': 'online' if ok else 'offline', 'ok': ok}), 200

@app.route('/api/v1/glpi/status', methods=['GET'])
def glpi_status():
    ok = checar_porta('10.199.43.26', 443) or checar_porta('127.0.0.1', 8088)
    return jsonify({'servico': 'glpi', 'status': 'online' if ok else 'offline', 'ok': ok}), 200

@app.route('/api/v1/openproject/status', methods=['GET'])
@app.route('/api/v1/openproject/sync_status', methods=['GET'])
def openproject_status():
    ok = checar_porta('143.107.108.115', 443) or checar_porta('127.0.0.1', 8090)
    return jsonify({'servico': 'openproject', 'status': 'online' if ok else 'offline', 'ok': ok}), 200

# -------------------------------------------------------------------------
# 2. GESTÃO DO POOL MULTI-IA
# -------------------------------------------------------------------------
def mascarar_chaves_recursivo(obj):
    if isinstance(obj, dict):
        novo = {}
        for k, v in obj.items():
            if any(termo in k.lower() for termo in ('apikey', 'api_key', 'chave', 'secret', 'token')) and isinstance(v, str):
                novo[k] = '***' if v else ''
            else:
                novo[k] = mascarar_chaves_recursivo(v)
        return novo
    elif isinstance(obj, list):
        return [mascarar_chaves_recursivo(item) for item in obj]
    return obj

def mascarar_chaves_recursivo(obj):
    if isinstance(obj, dict):
        novo = {}
        for k, v in obj.items():
            if any(termo in k.lower() for termo in ('apikey', 'api_key', 'chave', 'secret', 'token')) and isinstance(v, str):
                novo[k] = '***' if v else ''
            else:
                novo[k] = mascarar_chaves_recursivo(v)
        return novo
    elif isinstance(obj, list):
        return [mascarar_chaves_recursivo(item) for item in obj]
    return obj

def mesclar_preservando_segredos(novos, originais):
    if isinstance(novos, dict) and isinstance(originais, dict):
        for k, v in novos.items():
            if k in originais:
                if v == '***' or (isinstance(v, str) and v.startswith('***')):
                    novos[k] = originais[k]
                else:
                    novos[k] = mesclar_preservando_segredos(v, originais[k])
    elif isinstance(novos, list) and isinstance(originais, list):
        for i, item in enumerate(novos):
            if i < len(originais):
                novos[i] = mesclar_preservando_segredos(item, originais[i])
    return novos

def mascarar_chaves_recursivo(obj):
    if isinstance(obj, dict):
        novo = {}
        for k, v in obj.items():
            if any(termo in k.lower() for termo in ('apikey', 'api_key', 'chave', 'secret', 'token')) and isinstance(v, str):
                novo[k] = '***' if v else ''
            else:
                novo[k] = mascarar_chaves_recursivo(v)
        return novo
    elif isinstance(obj, list):
        return [mascarar_chaves_recursivo(item) for item in obj]
    return obj

def extrair_id_item(item):
    if isinstance(item, dict):
        # 1. ID ou Slot explícito
        if item.get('id'):
            return f"id:{item['id']}"
        if item.get('slot'):
            return f"slot:{item['slot']}"
        # 2. Chave composta modelo + endpoint para evitar colisão entre modelos no mesmo host
        mod = str(item.get('modelo') or item.get('model') or item.get('nome') or item.get('name') or '').strip().lower()
        ep = str(item.get('endpoint') or item.get('url') or item.get('baseUrl') or item.get('base_url') or '').strip().lower()
        if mod or ep:
            return f"mod:{mod}|ep:{ep}"
        itens_estaveis = {k: v for k, v in item.items() if not any(s in k.lower() for s in ('key', 'token', 'secret'))}
        return str(sorted(itens_estaveis.items()))
    return ''

def resolver_chave_real(identificador=None):
    cfg_path = localizar_config_pool()
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            itens = []
            if isinstance(dados, list):
                itens = dados
            elif isinstance(dados, dict):
                for k in ('ias', 'slots', 'models', 'pool'):
                    if isinstance(dados.get(k), list):
                        itens.extend(dados[k])
                if not itens:
                    itens = [dados]
            
            alvo = str(identificador or '').strip().lower()
            for it in itens:
                if isinstance(it, dict):
                    valores = [str(v).strip().lower() for k, v in it.items() if k in ('id', 'slot', 'modelo', 'model', 'nome', 'name') and v]
                    if alvo in valores or not alvo:
                        for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                            if it.get(k) and it[k] != '***':
                                return it[k]
            # Fallback para o primeiro slot com chave real
            for it in itens:
                if isinstance(it, dict):
                    for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                        if it.get(k) and it[k] != '***':
                            return it[k]
        except Exception:
            pass
    return os.getenv('NEWAPI_API_KEY') or os.getenv('NEW_API_KEY') or ''


def mascarar_chaves_recursivo(obj):
    if isinstance(obj, dict):
        novo = {}
        for k, v in obj.items():
            if any(termo in k.lower() for termo in ('apikey', 'api_key', 'chave', 'secret', 'token')) and isinstance(v, str):
                novo[k] = '***' if v else ''
            else:
                novo[k] = mascarar_chaves_recursivo(v)
        return novo
    elif isinstance(obj, list):
        return [mascarar_chaves_recursivo(item) for item in obj]
    return obj

def mesclar_preservando_segredos(novos, originais):
    if isinstance(novos, list) and isinstance(originais, list):
        mapa_originais = {}
        for orig in originais:
            chave_id = extrair_id_item(orig)
            if chave_id:
                mapa_originais[chave_id] = orig

        resultado = []
        for i, novo in enumerate(novos):
            chave_id = extrair_id_item(novo)
            orig_match = mapa_originais.get(chave_id) if chave_id else (originais[i] if i < len(originais) else None)
            if orig_match:
                resultado.append(mesclar_preservando_segredos(novo, orig_match))
            else:
                resultado.append(novo)
        return resultado
    elif isinstance(novos, dict) and isinstance(originais, dict):
        resultado = dict(novos)
        for k, v in novos.items():
            if k in originais:
                if v == '***' or (isinstance(v, str) and v.startswith('***')):
                    resultado[k] = originais[k]
                elif isinstance(v, (dict, list)):
                    resultado[k] = mesclar_preservando_segredos(v, originais[k])
        return resultado
    return novos


@app.route('/api/v1/ia/pool', methods=['GET', 'POST'])
def api_v1_ia_pool():
    cfg_path = localizar_config_pool()
    if request.method == 'POST':
        try:
            dados = request.get_json(force=True) or {}
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f_orig:
                        config_original = json.load(f_orig)
                    dados = mesclar_preservando_segredos(dados, config_original)
                except Exception:
                    pass
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            return jsonify({'sucesso': True, 'status': 'sucesso', 'mensagem': 'Pool salvo com sucesso!'})
        except Exception as e:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 200
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                pool_raw = json.load(f)
            return jsonify(mascarar_chaves_recursivo(pool_raw))
        except Exception:
            pass
    return jsonify({'status': 'padrao'})

@app.route('/api/v1/ia/testar_slot', methods=['POST'])
def api_v1_ia_testar_slot():
    try:
        t0 = time.time()
        dados = request.get_json(force=True) or {}
        raw_endpoint = dados.get('endpoint', 'http://127.0.0.1:3001/v1')
        endpoint = normalizar_endpoint_ia(raw_endpoint)
        api_key = dados.get('apiKey') or os.environ.get('NEWAPI_API_KEY', '')
        model = dados.get('model', 'qwen2.5:14b')
        slot = dados.get('slot', 'ia')

        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'ping'}],
            'max_tokens': 10
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            latencia = int((time.time() - t0) * 1000)
            return jsonify({
                'sucesso': True,
                'status': 'sucesso',
                'codigo': resp.status,
                'codigoHttp': resp.status,
                'latenciaMs': latencia,
                'latencia_ms': latencia,
                'mensagem': f'Slot {model} ativo ({latencia}ms)!'
            })
    except urllib.error.HTTPError as he:
        detalhe = he.read().decode('utf-8', errors='ignore') if he.fp else str(he)
        return jsonify({
            'sucesso': False,
            'status': 'erro',
            'erro': f'HTTP {he.code}: {he.reason}',
            'mensagem': f'Erro HTTP {he.code}: {detalhe[:120]}'
        }), 200
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'status': 'erro',
            'erro': str(e),
            'mensagem': f'Erro de conexao: {str(e)}'
        }), 200

@app.route('/api/v1/ia/chat', methods=['POST'])
def api_v1_ia_chat():
    try:
        dados = request.get_json(force=True) or {}
        mensagens = dados.get('mensagens') or dados.get('messages') or []
        ia_alvo = dados.get('ia', 'principal')
        endpoint = normalizar_endpoint_ia(dados.get('endpoint', 'http://127.0.0.1:3001/v1'))
        api_key = dados.get('apiKey') or os.environ.get('NEWAPI_API_KEY', '')
        model = dados.get('model', 'qwen2.5:14b' if ia_alvo == 'principal' else 'qwen2.5:7b')

        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': mensagens,
            'temperature': 0.3,
            'max_tokens': 2000
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            corpo = json.loads(resp.read().decode('utf-8'))
            return jsonify({
                'sucesso': True,
                'status': 'sucesso',
                'resposta': corpo['choices'][0]['message']['content'],
                'modelo': model,
                'ia': ia_alvo
            })
    except Exception as e:
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 200

# -------------------------------------------------------------------------
# 3. CONECTOR REAL OPENPROJECT (API v3 COM LOCKVERSION & ATIVIDADES)
# -------------------------------------------------------------------------
def obter_token_openproject():
    token = os.environ.get('OPENPROJECT_API_TOKEN', '').strip()
    if token:
        return token
    for caminho in ['openproject_token.txt', 'backend/openproject_token.txt', 'data/openproject_token.txt']:
        if os.path.exists(caminho):
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    t = f.read().strip()
                    if t:
                        return t
            except Exception:
                pass
    return ''

def sincronizar_card_openproject_real(card_id, comentario="", descricao=None):
    token = obter_token_openproject()
    op_base_url = os.environ.get('OPENPROJECT_URL', 'https://projetos.spaguas.sp.gov.br').rstrip('/')

    if not token:
        return {
            'sucesso': False,
            'status': 'aviso',
            'card_id': card_id,
            'mensagem': 'Token do OpenProject não configurado (adicione em openproject_token.txt ou .env)'
        }

    auth_str = f"apikey:{token}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json',
        'User-Agent': 'CockpitGTI/11.0'
    }

    ctx = ssl.create_default_context()
    if not VERIFY_SSL:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        get_url = f"{op_base_url}/api/v3/work_packages/{card_id}"
        req_get = urllib.request.Request(get_url, headers=headers, method='GET')
        with urllib.request.urlopen(req_get, timeout=8, context=ctx) as resp:
            wp_data = json.loads(resp.read().decode('utf-8'))
            lock_version = wp_data.get('lockVersion', 0)

        novo_lock = lock_version + 1
        if descricao:
            patch_url = f"{op_base_url}/api/v3/work_packages/{card_id}"
            payload_patch = {'lockVersion': lock_version, 'description': {'raw': descricao}}
            req_patch = urllib.request.Request(
                patch_url,
                data=json.dumps(payload_patch).encode('utf-8'),
                headers=headers,
                method='PATCH'
            )
            with urllib.request.urlopen(req_patch, timeout=10, context=ctx) as resp_p:
                p_res = json.loads(resp_p.read().decode('utf-8'))
                novo_lock = p_res.get('lockVersion', novo_lock)

        if comentario:
            act_url = f"{op_base_url}/api/v3/work_packages/{card_id}/activities"
            payload_act = {'comment': {'raw': comentario}}
            req_act = urllib.request.Request(
                act_url,
                data=json.dumps(payload_act).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req_act, timeout=8, context=ctx):
                pass

        return {
            'sucesso': True,
            'status': 'sucesso',
            'card_id': card_id,
            'lockVersion': novo_lock,
            'mensagem': f'Card #{card_id} sincronizado com sucesso no OpenProject (lockVersion: {novo_lock})'
        }
    except urllib.error.HTTPError as he:
        detalhe = he.read().decode('utf-8', errors='ignore') if he.fp else str(he)
        return {
            'sucesso': False,
            'status': 'erro',
            'card_id': card_id,
            'mensagem': f'Erro HTTP {he.code} no OpenProject: {detalhe[:140]}'
        }
    except Exception as e:
        return {
            'sucesso': False,
            'status': 'erro',
            'card_id': card_id,
            'mensagem': f'Falha de rede ao contatar OpenProject: {str(e)}'
        }

@app.route('/api/v1/openproject/sync_card', methods=['POST'])
def api_v1_op_sync_card():
    try:
        dados = request.get_json(force=True) or {}
        # Aceita tanto card_id quanto cardId (compatibilidade UI)
        card_id = dados.get('card_id') or dados.get('cardId')
        if not card_id:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'card_id ou cardId obrigatório'}), 400
        comentario = dados.get('comentario', '')
        descricao = dados.get('descricao', None)
        resultado = sincronizar_card_openproject_real(card_id, comentario=comentario, descricao=descricao)
        return jsonify(resultado), (200 if resultado.get('sucesso') else 400)
    except Exception as e:
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 500

@app.route('/api/v1/openproject/sync_batch', methods=['POST'])
def api_v1_op_sync_batch():
    dados = request.get_json(force=True) or {}
    itens = dados.get('itens') or dados.get('cards') or []
    processados = []
    
    op_base_url = os.getenv('OPENPROJECT_URL', 'https://openproject.spaguas.sp.gov.br')
    op_token = os.getenv('OPENPROJECT_API_TOKEN') or os.getenv('OPENPROJECT_API_KEY') or ''
    headers = {
        'Authorization': f"Basic {base64.b64encode(f'apikey:{op_token}'.encode()).decode()}",
        'Content-Type': 'application/json',
        'User-Agent': 'CockpitGTI/11.0'
    }
    ctx = ssl.create_default_context()
    if not VERIFY_SSL:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    for c in itens:
        c_id = c.get('id') or c.get('card_id') or c.get('cardId')
        if c_id:
            try:
                patch_url = f"{op_base_url}/api/v3/work_packages/{c_id}"
                payload_patch = {'lockVersion': c.get('lockVersion', 1)}
                
                # Conversão padrão OpenProject v3 para descrição ({"raw": ...})
                desc = c.get('descricao') or c.get('description')
                if desc:
                    payload_patch['description'] = desc if isinstance(desc, dict) else {'raw': str(desc)}
                    
                # Conversão para subject
                sub = c.get('titulo') or c.get('subject')
                if sub:
                    payload_patch['subject'] = sub

                for k, v in c.items():
                    if k not in ('id', 'card_id', 'cardId', 'lockVersion', 'descricao', 'description', 'titulo', 'subject'):
                        payload_patch[k] = v
                
                body_patch = json.dumps(payload_patch).encode('utf-8')
                req = urllib.request.Request(patch_url, data=body_patch, headers=headers, method='PATCH')
                with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                    wp_data = json.loads(resp.read().decode())
                processados.append({'card_id': c_id, 'sucesso': True, 'status': 'sincronizado', 'lockVersion': wp_data.get('lockVersion', 1)})
            except Exception as e:
                processados.append({'card_id': c_id, 'sucesso': False, 'status': 'erro_conexao', 'mensagem': str(e)})

    todos_sucesso = all(p.get('sucesso', False) for p in processados) if processados else True
    return jsonify({
        'sucesso': todos_sucesso,
        'total_processado': len(processados),
        'itens': processados
    }), (200 if todos_sucesso else 502)


@app.route('/api/v1/openproject/historico_agendado_v2', methods=['GET'])
def api_v1_op_historico():
    for c in ['registro_execucao_agendada.json', 'data/registro_execucao_agendada.json']:
        if os.path.exists(c):
            try:
                with open(c, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception:
                pass
    return jsonify({'sucesso': True, 'historico': []}), 200

# -------------------------------------------------------------------------
# 4. CONECTOR GLPI 10 (LEITURA ESTRUTURADA DE TICKETS E ATIVOS)
# -------------------------------------------------------------------------
@app.route('/api/v1/glpi/tickets', methods=['GET'])
def api_v1_glpi_tickets():
    tickets = []
    glpi_url = os.getenv('GLPI_URL', 'https://glpi.spaguas.sp.gov.br')
    glpi_app_token = os.getenv('GLPI_APP_TOKEN', '')
    glpi_user_token = os.getenv('GLPI_USER_TOKEN', '')

    for c in ['glpi_producao_cache.json', 'data/glpi_producao_cache.json', 'backend/glpi_producao_cache.json']:
        if os.path.exists(c):
            try:
                with open(c, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    if isinstance(dados, list):
                        tickets = dados
                    elif isinstance(dados, dict):
                        tickets = dados.get('tickets') or dados.get('chamados') or dados.get('data') or []
                    if tickets:
                        break
            except Exception:
                pass

    if not tickets and glpi_url and glpi_app_token:
        try:
            req_glpi = urllib.request.Request(
                f"{glpi_url}/apirest.php/Ticket",
                headers={'App-Token': glpi_app_token, 'Session-Token': glpi_user_token},
                method='GET'
            )
            ctx = ssl.create_default_context()
            if not VERIFY_SSL:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req_glpi, timeout=5, context=ctx) as r:
                tickets = json.loads(r.read().decode())
        except Exception as e:
            return jsonify({'sucesso': False, 'status': 'erro_conexao', 'mensagem': f'Falha ao conectar com GLPI: {str(e)}', 'tickets': []}), 502

    return jsonify({
        'sucesso': True,
        'origem': 'GLPI 10 Produção (Cache Estruturado)' if tickets else 'GLPI Produção',
        'total': len(tickets),
        'tickets': tickets
    }), 200


# -------------------------------------------------------------------------
# 5. DOCUMENTAÇÃO OFICIAL DINÂMICA (LEITURA DE DOCS/*.MD)
# -------------------------------------------------------------------------
@app.route('/api/v1/docs/<doc_id>', methods=['GET'])
def api_v1_obter_documento(doc_id):
    mapa = {
        'usuario': 'MANUAL_DO_USUARIO.md',
        'tecnica': 'DOCUMENTACAO_TECNICA.md',
        'github': 'GUIA_PUBLICACAO_GITHUB.md',
        'readme': 'README.md'
    }
    arquivo = mapa.get(doc_id.lower())
    if not arquivo:
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Documento não encontrado'}), 404

    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(base, 'docs', arquivo),
        os.path.join(base, arquivo),
        os.path.abspath(os.path.join('docs', arquivo)),
        os.path.abspath(arquivo)
    ]
    for c in candidatos:
        if os.path.exists(c):
            try:
                with open(c, 'r', encoding='utf-8') as f:
                    return jsonify({
                        'sucesso': True,
                        'status': 'sucesso',
                        'doc_id': doc_id,
                        'arquivo': arquivo,
                        'conteudo_md': f.read()
                    })
            except Exception as e:
                return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 500

    return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Arquivo não localizado em disco'}), 404

if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
