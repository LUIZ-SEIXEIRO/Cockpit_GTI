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
def resolver_chave_real(modelo=None, slot=None):
    cfg_path = localizar_config_pool()
    if not os.path.exists(cfg_path):
        return os.getenv('NEWAPI_API_KEY') or os.getenv('NEW_API_KEY') or ''

    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        slots_dict = dados.get('ias', {})
        if isinstance(slots_dict, dict):
            itens_com_chave = list(slots_dict.items())
        elif isinstance(slots_dict, list):
            itens_com_chave = [(it.get('id', str(i)), it) for i, it in enumerate(slots_dict) if isinstance(it, dict)]
        elif isinstance(dados, list):
            itens_com_chave = [(it.get('id', str(i)), it) for i, it in enumerate(dados) if isinstance(it, dict)]
        else:
            itens_com_chave = [('principal', dados)]

        # 1. Se informou um slot específico: IDENTIFICA O SLOT EXATO
        if slot:
            alvo_s = str(slot).strip().lower()
            alvo_m = str(modelo).strip().lower() if modelo else None
            slot_encontrado = None

            # 1.1 Prioridade absoluta: Match por ID explícito do item (segue o ID, não a posição do slot)
            for s_key, it in itens_com_chave:
                if isinstance(it, dict):
                    it_id = str(it.get('id') or it.get('slot') or '').strip().lower()
                    if it_id == alvo_s:
                        slot_encontrado = it
                        break

            # 1.2 Se não achou por ID do item, busca pelo nome/chave do slot no dict
            if not slot_encontrado:
                for s_key, it in itens_com_chave:
                    if str(s_key).strip().lower() == alvo_s:
                        slot_encontrado = it
                        break

            # SE LOCALIZOU O SLOT ESPECIFICADO:
            if slot_encontrado:
                if alvo_m:
                    m_it = str(slot_encontrado.get('agent') or slot_encontrado.get('modelo') or slot_encontrado.get('model') or '').strip().lower()
                    if m_it and m_it != alvo_m:
                        return ''

                # Retorna estritamente a chave deste slot (ou vazio se não tiver)
                # NUNCA pega emprestada chave de outro slot com o mesmo modelo!
                for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                    v = slot_encontrado.get(k)
                    if v and v != '***':
                        return v
                return ''

        # 2. Se NÃO informou slot: busca no pool pelo modelo
        if modelo:
            alvo_m = str(modelo).strip().lower()
            for s_key, it in itens_com_chave:
                if isinstance(it, dict):
                    for campo in ('agent', 'modelo', 'model', 'nome'):
                        if str(it.get(campo) or '').strip().lower() == alvo_m:
                            for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                                v = it.get(k)
                                if v and v != '***':
                                    return v

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
    if isinstance(novos, dict) and isinstance(originais, dict):
        resultado = dict(novos)
        orig_ias = originais.get('ias')
        nov_ias = novos.get('ias')

        if orig_ias and nov_ias and isinstance(orig_ias, dict) and isinstance(nov_ias, dict):
            consumidos_originais = set()
            ias_mescladas = {}

            for s_key, s_val in nov_ias.items():
                if isinstance(s_val, dict):
                    item_novo = dict(s_val)
                    chave_env = item_novo.get('apiKey') or item_novo.get('api_key')
                    if chave_env == '***' or (isinstance(chave_env, str) and chave_env.startswith('***')):
                        m_novo = item_novo.get('agent') or item_novo.get('modelo') or item_novo.get('model') or ''
                        id_novo = item_novo.get('id')
                        match_key = None

                        # 1. PRIORIDADE: Match exato por (ID e MODELO) - a chave segue o ID do modelo
                        if id_novo and m_novo:
                            for orig_k, orig_v in orig_ias.items():
                                if orig_k not in consumidos_originais and isinstance(orig_v, dict):
                                    id_orig = orig_v.get('id') or orig_k
                                    m_orig = orig_v.get('agent') or orig_v.get('modelo') or orig_v.get('model') or ''
                                    if id_orig == id_novo and m_orig == m_novo:
                                        match_key = orig_k
                                        break

                        # 2. Se mudou de slot mantendo o mesmo modelo: pareia com original de mesmo modelo
                        if not match_key and m_novo:
                            for orig_k, orig_v in orig_ias.items():
                                if orig_k not in consumidos_originais and isinstance(orig_v, dict):
                                    m_orig = orig_v.get('agent') or orig_v.get('modelo') or orig_v.get('model') or ''
                                    if m_orig == m_novo:
                                        match_key = orig_k
                                        break

                        # 3. Se recuperou match válido
                        if match_key:
                            consumidos_originais.add(match_key)
                            orig_item = orig_ias[match_key]
                            k_orig = orig_item.get('apiKey') or orig_item.get('api_key')
                            if k_orig and k_orig != '***':
                                if 'apiKey' in item_novo: item_novo['apiKey'] = k_orig
                                if 'api_key' in item_novo: item_novo['api_key'] = k_orig
                        else:
                            # Modelo novo sem correspondência: NÃO herda chave anterior
                            if 'apiKey' in item_novo and item_novo['apiKey'] == '***': item_novo['apiKey'] = ''
                            if 'api_key' in item_novo and item_novo['api_key'] == '***': item_novo['api_key'] = ''

                    ias_mescladas[s_key] = item_novo
                else:
                    ias_mescladas[s_key] = s_val
            resultado['ias'] = ias_mescladas

        elif orig_ias and nov_ias and isinstance(orig_ias, list) and isinstance(nov_ias, list):
            resultado['ias'] = mesclar_preservando_segredos(nov_ias, orig_ias)

        for k, v in novos.items():
            if k != 'ias':
                if k in originais:
                    if v == '***' or (isinstance(v, str) and v.startswith('***')):
                        resultado[k] = originais[k]
                    elif isinstance(v, (dict, list)):
                        resultado[k] = mesclar_preservando_segredos(v, originais[k])
                else:
                    resultado[k] = v
        return resultado

    elif isinstance(novos, list) and isinstance(originais, list):
        usados = set()
        resultado = []
        for novo in novos:
            if isinstance(novo, dict):
                it = dict(novo)
                chave = it.get('apiKey') or it.get('api_key')
                if chave == '***' or (isinstance(chave, str) and chave.startswith('***')):
                    novo_id = str(it['id']).strip().lower() if it.get('id') else None
                    novo_mod = str(it.get('agent') or it.get('modelo') or it.get('model') or '').strip().lower()
                    match = None
                    if novo_id:
                        for idx, orig in enumerate(originais):
                            if idx not in usados and isinstance(orig, dict) and str(orig.get('id') or '').strip().lower() == novo_id:
                                match = orig
                                usados.add(idx)
                                break
                    if not match and novo_mod:
                        for idx, orig in enumerate(originais):
                            if idx not in usados and isinstance(orig, dict):
                                orig_mod = str(orig.get('agent') or orig.get('modelo') or orig.get('model') or '').strip().lower()
                                if orig_mod == novo_mod:
                                    match = orig
                                    usados.add(idx)
                                    break
                    if match:
                        k_orig = match.get('apiKey') or match.get('api_key')
                        if k_orig and k_orig != '***':
                            if 'apiKey' in it: it['apiKey'] = k_orig
                            if 'api_key' in it: it['api_key'] = k_orig
                    else:
                        if it.get('apiKey') == '***': it['apiKey'] = ''
                        if it.get('api_key') == '***': it['api_key'] = ''
                resultado.append(it)
            else:
                resultado.append(novo)
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
        model = dados.get('model') or dados.get('agent') or 'qwen2.5:14b'
        slot = dados.get('slot', 'ia')

        api_key = dados.get('apiKey') or dados.get('api_key') or ''
        if not api_key or api_key == '***':
            api_key = resolver_chave_real(model, slot)

        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'ping'}],
            'max_tokens': 10
        }
        headers_req = {'Content-Type': 'application/json'}
        if api_key and api_key.strip():
            headers_req['Authorization'] = f'Bearer {api_key.strip()}'

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers_req
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            latencia = int((time.time() - t0) * 1000)
            return jsonify({
                'sucesso': True,
                'status': 'sucesso',
                'codigo': resp.status,
                'codigoHttp': resp.status,
                'latenciaMs': latencia,
                'resposta': 'pong'
            }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 500


@app.route('/api/v1/ia/chat', methods=['POST'])
def api_v1_ia_chat():
    try:
        dados = request.get_json(force=True) or {}
        mensagens = dados.get('mensagens') or dados.get('messages') or []
        ia_alvo = dados.get('ia', 'principal')
        endpoint = normalizar_endpoint_ia(dados.get('endpoint', 'http://127.0.0.1:3001/v1'))
        model = dados.get('model', 'qwen2.5:14b' if ia_alvo == 'principal' else 'qwen2.5:7b')
        slot_id = dados.get('slot') or ia_alvo

        api_key = dados.get('apiKey') or dados.get('api_key') or ''
        if not api_key or api_key == '***':
            api_key = resolver_chave_real(model, slot_id)

        url = endpoint + '/chat/completions'
        payload = {
            'model': model,
            'messages': mensagens,
            'temperature': 0.3,
            'max_tokens': 2000
        }
        headers_req = {'Content-Type': 'application/json'}
        if api_key and api_key.strip():
            headers_req['Authorization'] = f'Bearer {api_key.strip()}'

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers_req
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            resp_dados = json.loads(resp.read().decode())
            return jsonify(resp_dados), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 500


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
                payload_patch = {'lockVersion': c.get('lockVersion', 1)}                # Conversão padrão OpenProject v3 para descrição (permite valor vazio para limpeza)
                if 'descricao' in c or 'description' in c:
                    desc_val = c.get('descricao') if 'descricao' in c else c.get('description')
                    if isinstance(desc_val, dict):
                        payload_patch['description'] = desc_val
                    elif desc_val is None or desc_val == '':
                        payload_patch['description'] = {'raw': ''}
                    else:
                        payload_patch['description'] = {'raw': str(desc_val)}
                    
                # Conversão para subject
                if 'titulo' in c or 'subject' in c:
                    sub_val = c.get('titulo') if 'titulo' in c else c.get('subject')
                    payload_patch['subject'] = '' if sub_val is None else str(sub_val)

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
