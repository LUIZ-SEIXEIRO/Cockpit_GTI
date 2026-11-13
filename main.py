# -*- coding: utf-8 -*-
from urllib.parse import urlsplit
from functools import wraps
import hmac
import os
import json
import time
import socket
import ssl
import base64
import logging
import stat
import tempfile
import uuid
import urllib.request
import urllib.error
from datetime import timedelta
from flask import Flask, request, jsonify, send_from_directory, g, has_request_context, redirect, session
from werkzeug.exceptions import HTTPException

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'),
    static_url_path='/static',
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('COCKPIT_SESSION_SECRET') or None
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('COCKPIT_SESSION_COOKIE_SECURE', 'true').lower() in ('true', '1')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
logging.getLogger('werkzeug').setLevel(logging.WARNING)


@app.errorhandler(413)
def request_too_large(_erro):
    return jsonify({
        'sucesso': False,
        'status': 'erro',
        'mensagem': 'Requisição excede o limite de tamanho permitido.',
    }), 413


@app.errorhandler(Exception)
def handle_unhandled_exception(erro):
    if isinstance(erro, HTTPException):
        return erro
    return resposta_erro_interno(
        'unhandled_request_error',
        erro,
        'Falha interna ao processar a solicitação.',
    )

def normalizar_origem(origem):
    try:
        parsed = urlsplit(origem)
        scheme = parsed.scheme.lower()
        host = parsed.hostname.lower() if parsed.hostname else ''
        if (
            scheme not in ('http', 'https')
            or not host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or parsed.netloc.endswith(':')
        ):
            return None
        port = parsed.port
        if (scheme == 'http' and port == 80) or (scheme == 'https' and port == 443):
            port = None
        host_netloc = f'[{host}]' if ':' in host else host
        return f'{scheme}://{host_netloc}' + (f':{port}' if port is not None else '')
    except (AttributeError, TypeError, ValueError):
        return None

def requer_autenticacao(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if not token_configurado():
            return jsonify({'sucesso': False, 'erro': 'Autenticação não configurada.'}), 401
        if not requisicao_autenticada():
            return jsonify({'sucesso': False, 'erro': 'Acesso não autorizado.'}), 401
        return f(*args, **kwargs)
    return decorado


ORIGENS_PADRAO = {
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'http://100.103.100.98:5000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://100.103.100.98:3001',
    'https://cockpit.spaguas.gov.br',
}
ALLOWED_ORIGINS = {normalizar_origem(origem) for origem in ORIGENS_PADRAO}
ALLOWED_ORIGINS.discard(None)
for origem_configurada in os.environ.get('ALLOWED_ORIGINS', '').split(','):
    origem_normalizada = normalizar_origem(origem_configurada.strip())
    if origem_normalizada:
        ALLOWED_ORIGINS.add(origem_normalizada)

ROTAS_AUTENTICADAS = {
    '/api/v1/ia/pool',
    '/api/v1/ia/chat',
    '/api/v1/ia/testar_slot',
    '/api/v1/ia/revisar_processo',
    '/api/v1/openproject/sync_card',
    '/api/v1/openproject/sync_batch',
    '/api/v1/openproject/historico_agendado_v2',
    '/api/v1/openproject/historico_agendado',
    '/api/v1/glpi/tickets',
    '/api/v1/processos',
    '/api/v1/sei/status',
    '/api/v1/sei/sessao',
    '/api/v1/sei/processos',
    '/api/v1/sei/buscar',
}


def validar_origem_estrita(origem):
    normalizada = normalizar_origem(origem)
    return normalizada is not None and normalizada in ALLOWED_ORIGINS


def token_configurado():
    return bool(obter_token_servidor())


def sessao_autenticada():
    return bool(os.getenv('COCKPIT_SESSION_SECRET')) and session.get('cockpit_authenticated') is True


def obter_token_servidor():
    return (os.getenv('COCKPIT_API_TOKEN') or '').strip() or (os.getenv('API_TOKEN') or '').strip()


def requisicao_autenticada():
    token_esperado = obter_token_servidor()
    if not token_esperado:
        return False
    auth_header = request.headers.get('Authorization', '').strip()
    esquema, separador, credencial = auth_header.partition(' ')
    bearer = credencial.strip() if separador and esquema.lower() == 'bearer' else ''
    token_fornecido = bearer or request.headers.get('X-Cockpit-Token', '').strip() or request.headers.get('X-API-Key', '').strip()
    return (
        bool(token_fornecido) and hmac.compare_digest(
            token_fornecido.encode('utf-8'),
            token_esperado.encode('utf-8'),
        )
    ) or sessao_autenticada()


def registrar_falha_operacional(evento, excecao):
    app.logger.error(
        'application_error %s',
        json.dumps({
            'event': evento,
            'request_id': getattr(g, 'request_id', 'unavailable') if has_request_context() else 'unavailable',
            'exception_type': type(excecao).__name__,
        }, separators=(',', ':')),
    )


def resposta_erro_interno(evento, excecao, mensagem):
    if isinstance(excecao, HTTPException) and excecao.code == 413:
        return request_too_large(excecao)
    registrar_falha_operacional(evento, excecao)
    return jsonify({
        'sucesso': False,
        'status': 'erro',
        'mensagem': mensagem,
        'requestId': getattr(g, 'request_id', None),
    }), 500

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


def obter_alvo_url_servico(variavel, padrao):
    try:
        endpoint = os.getenv(variavel) or padrao
        parsed = urlsplit(endpoint)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            return '', None
        porta = parsed.port or (443 if parsed.scheme == 'https' else 80)
        return parsed.hostname, porta
    except (TypeError, ValueError):
        return '', None


def checar_alvo_servico(host, porta):
    if not host or not porta:
        return False
    return checar_porta(host, porta)


def status_servico(servico, host, porta):
    if not host or not porta:
        return jsonify({
            'servico': servico,
            'status': 'nao_configurado',
            'ok': False,
        }), 200
    ok = checar_alvo_servico(host, porta)
    return jsonify({
        'servico': servico,
        'status': 'online' if ok else 'offline',
        'ok': ok,
    }), 200

# -------------------------------------------------------------------------
# SEGURANÇA, PRIVACIDADE E OBSERVABILIDADE
# -------------------------------------------------------------------------
COCKPIT_API_TOKEN = os.getenv("COCKPIT_API_TOKEN") or os.getenv("API_TOKEN")
API_TOKEN = COCKPIT_API_TOKEN
OPENPROJECT_API_TOKEN = os.getenv("OPENPROJECT_API_TOKEN") or os.getenv("OPENPROJECT_API_KEY")
OPENPROJECT_API_KEY = OPENPROJECT_API_TOKEN
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1")
if not VERIFY_SSL:
    app.logger.warning('tls_certificate_verification_disabled')

@app.after_request
def aplicar_controles_de_resposta(response):
    origin = request.headers.get('Origin', '')
    origem_normalizada = normalizar_origem(origin)
    if origem_normalizada and origem_normalizada in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origem_normalizada
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Cockpit-Token, X-API-Key'
            )
            response.headers['Access-Control-Max-Age'] = '600'

    vary = {item.strip() for item in response.headers.get('Vary', '').split(',') if item.strip()}
    vary.add('Origin')
    response.headers['Vary'] = ', '.join(sorted(vary))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    if request.path.startswith('/api/') or request.path in ('/', '/painel', '/frontend/painel.html', '/static/painel.html'):
        response.headers['Cache-Control'] = 'no-store'
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'

    request_id = getattr(g, 'request_id', None)
    if request_id:
        response.headers['X-Request-ID'] = request_id
        elapsed_ms = round((time.perf_counter() - g.request_started) * 1000, 2)
        app.logger.info(
            'http_request %s',
            json.dumps({
                'request_id': request_id,
                'method': request.method,
                'endpoint': request.endpoint or 'unmatched',
                'status': response.status_code,
                'duration_ms': elapsed_ms,
            }, separators=(',', ':')),
        )

    return response

@app.before_request
def iniciar_requisicao_e_autenticar():
    g.request_id = uuid.uuid4().hex
    g.request_started = time.perf_counter()

    if request.method == 'OPTIONS':
        origin = request.headers.get('Origin', '')
        if origin and not validar_origem_estrita(origin):
            return jsonify({'sucesso': False, 'mensagem': 'Origem não autorizada.'}), 403
        return '', 204

    if request.path in ('/', '/painel', '/frontend/painel.html', '/static/painel.html') or request.path.startswith('/frontend/'):
        if not sessao_autenticada():
            return redirect('/login', code=303)

    if request.path in ROTAS_AUTENTICADAS:
        if not token_configurado():
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Autenticação não configurada.'}), 401
        if not requisicao_autenticada():
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Acesso não autorizado.'}), 401


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

@app.route('/frontend/<path:filename>')
def servir_estaticos(filename):
    base = os.path.dirname(os.path.abspath(__file__))
    pastas = [os.path.join(base, 'frontend'), os.path.abspath('frontend')]
    for p in pastas:
        if os.path.exists(os.path.join(p, filename)):
            return send_from_directory(p, filename)
    return "Arquivo não encontrado", 404


@app.route('/login', methods=['GET'])
def rota_login():
    if sessao_autenticada():
        return redirect('/', code=303)
    return '''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Acesso institucional — Cockpit GTI</title>
  <style>
    *{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;
    background:#f1f5f9;color:#0f172a;font:16px system-ui,sans-serif}
    main{width:min(100%,420px);padding:28px;background:#fff;border:1px solid #cbd5e1;border-radius:8px}
    h1{margin:0 0 8px;font-size:1.35rem}p{color:#475569;line-height:1.5}
    label{display:block;margin:20px 0 6px;font-weight:650}
    input,button{width:100%;padding:11px;border:1px solid #94a3b8;border-radius:6px;font:inherit}
    button{margin-top:14px;background:#0544cf;color:#fff;border-color:#0544cf;font-weight:700;cursor:pointer}
    #erro{min-height:1.5em;color:#b91c1c}
  </style>
</head>
<body>
  <main>
    <h1>Cockpit GTI — acesso restrito</h1>
    <p>Informe o token de acesso configurado pelo administrador. A sessão expira após oito horas.</p>
    <form id="login">
      <label for="token">Token institucional</label>
      <input id="token" name="token" type="password" autocomplete="current-password" required>
      <p id="erro" role="alert"></p>
      <button type="submit">Entrar</button>
    </form>
  </main>
  <script>
    document.getElementById('login').addEventListener('submit', async function(event) {
      event.preventDefault();
      const erro = document.getElementById('erro');
      erro.textContent = '';
      try {
        const response = await fetch('/api/v1/session', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({token: document.getElementById('token').value})
        });
        if (!response.ok) throw new Error('Acesso negado ou autenticação indisponível.');
        window.location.replace('/');
      } catch (error) {
        erro.textContent = error.message || 'Não foi possível iniciar a sessão.';
      }
    });
  </script>
</body>
</html>'''


@app.route('/api/v1/session', methods=['GET', 'POST', 'DELETE'])
def api_v1_session():
    if request.method == 'GET':
        return jsonify({'authenticated': sessao_autenticada()}), 200
    if request.method == 'DELETE':
        if not os.getenv('COCKPIT_SESSION_SECRET'):
            return jsonify({
                'sucesso': False,
                'mensagem': 'Autenticação web indisponível: configure COCKPIT_SESSION_SECRET.',
            }), 503
        session.clear()
        return jsonify({'authenticated': False}), 200

    if not os.getenv('COCKPIT_SESSION_SECRET'):
        return jsonify({
            'sucesso': False,
            'mensagem': 'Autenticação web indisponível: configure COCKPIT_SESSION_SECRET.',
        }), 503
    token_esperado = obter_token_servidor()
    dados = request.get_json(silent=True)
    token_fornecido = dados.get('token') if isinstance(dados, dict) else None
    if not token_esperado or not isinstance(token_fornecido, str) or not hmac.compare_digest(
        token_fornecido.encode('utf-8'),
        token_esperado.encode('utf-8'),
    ):
        return jsonify({'sucesso': False, 'mensagem': 'Credencial inválida.'}), 401

    session.clear()
    session['cockpit_authenticated'] = True
    session.permanent = True
    return jsonify({'authenticated': True}), 200

def validar_endpoints_payload_pool(dados):
    ias = dados.get('ias') if isinstance(dados, dict) else dados
    itens = list(ias.values()) if isinstance(ias, dict) else (ias if isinstance(ias, list) else [])
    for it in itens:
        if isinstance(it, dict):
            ep = it.get('endpoint') or it.get('url')
            if ep is not None and ep != '':
                motor_ia.validar_endpoint_ia(ep)


def normalizar_endpoint_ia(endpoint):
    if endpoint is None or endpoint == '':
        return motor_ia.obter_endpoint_padrao()
    if not isinstance(endpoint, str):
        raise ValueError('Endpoint de IA deve ser uma string.')
    return motor_ia.validar_endpoint_ia(endpoint)

def localizar_config_pool():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.environ.get(
        'IA_POOL_CONFIG_FILE',
        os.path.join(base, 'data', 'config_pool_ias.local.json'),
    )


def localizar_modelo_pool():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'config_pool_ias.json')


def chave_pool_configurada(valor):
    return (
        isinstance(valor, str)
        and valor.strip() not in ('', '***', 'sk-CHAVE-SANITIZADA-INSTITUCIONAL')
    )


def salvar_json_atomico(caminho, dados, permissoes):
    diretorio = os.path.dirname(caminho) or '.'
    os.makedirs(diretorio, exist_ok=True)
    descritor, temporario = tempfile.mkstemp(prefix='.pool-ias-', suffix='.tmp', dir=diretorio)
    try:
        if permissoes is not None and hasattr(os, 'fchmod'):
            os.fchmod(descritor, permissoes)
        arquivo = os.fdopen(descritor, 'w', encoding='utf-8')
        descritor = None
        with arquivo:
            json.dump(dados, arquivo, indent=2, ensure_ascii=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if descritor is not None:
            os.close(descritor)
        if os.path.exists(temporario):
            os.remove(temporario)


def salvar_pool_privado(caminho, dados):
    salvar_json_atomico(caminho, dados, 0o600)


def remover_segredos_modelo_pool(caminho, dados):
    permissoes = stat.S_IMODE(os.stat(caminho).st_mode)
    salvar_json_atomico(caminho, mascarar_chaves_recursivo(dados), permissoes)


def garantir_pool_privado_migrado():
    caminho_privado = localizar_config_pool()
    if os.path.exists(caminho_privado):
        return caminho_privado
    caminho_modelo = localizar_modelo_pool()
    if not os.path.exists(caminho_modelo):
        return caminho_privado
    with open(caminho_modelo, 'r', encoding='utf-8') as arquivo:
        dados_modelo = json.load(arquivo)
    salvar_pool_privado(caminho_privado, dados_modelo)
    remover_segredos_modelo_pool(caminho_modelo, dados_modelo)
    return caminho_privado


# -------------------------------------------------------------------------
# 1. TELEMETRIA E HEALTH CHECKS INDIVIDUAIS
# -------------------------------------------------------------------------
@app.route('/api/v1/telemetria', methods=['GET'])
def rota_telemetria():
    mariadb_host = (os.getenv('MARIADB_HOST') or os.getenv('DB_HOST') or '').strip()
    try:
        mariadb_port = int(os.getenv('MARIADB_PORT') or os.getenv('DB_PORT') or '3306')
    except ValueError:
        mariadb_port = None
    ollama = obter_alvo_url_servico('OLLAMA_URL', 'http://ollama:11434')
    glpi = obter_alvo_url_servico('GLPI_URL', 'https://glpi.spaguas.sp.gov.br')
    openproject = obter_alvo_url_servico('OPENPROJECT_URL', 'https://openproject.spaguas.sp.gov.br')
    new_api = obter_alvo_url_servico('NEW_API_URL', 'http://new-api:3000/v1')
    status = {
        'mariadb': checar_alvo_servico(mariadb_host, mariadb_port),
        'ollama': checar_alvo_servico(*ollama),
        'glpi': checar_alvo_servico(*glpi),
        'openproject': checar_alvo_servico(*openproject),
        'newapi': checar_alvo_servico(*new_api),
    }
    return jsonify(status), 200

@app.route('/api/v1/mariadb/status', methods=['GET'])
def mariadb_status():
    host = (os.getenv('MARIADB_HOST') or os.getenv('DB_HOST') or '').strip()
    try:
        porta = int(os.getenv('MARIADB_PORT') or os.getenv('DB_PORT') or '3306')
    except ValueError:
        porta = None
    return status_servico('mariadb', host, porta)

@app.route('/api/v1/ia/status', methods=['GET'])
@app.route('/api/v1/newapi/status', methods=['GET'])
def ia_status():
    host, porta = obter_alvo_url_servico('NEW_API_URL', 'http://new-api:3000/v1')
    return status_servico('new-api', host, porta)

@app.route('/api/v1/ollama/status', methods=['GET'])
def ollama_status():
    host, porta = obter_alvo_url_servico('OLLAMA_URL', 'http://ollama:11434')
    return status_servico('ollama', host, porta)

@app.route('/api/v1/glpi/status', methods=['GET'])
def glpi_status():
    host, porta = obter_alvo_url_servico('GLPI_URL', 'https://glpi.spaguas.sp.gov.br')
    return status_servico('glpi', host, porta)

@app.route('/api/v1/openproject/status', methods=['GET'])
@app.route('/api/v1/openproject/sync_status', methods=['GET'])
def openproject_status():
    host, porta = obter_alvo_url_servico('OPENPROJECT_URL', 'https://openproject.spaguas.sp.gov.br')
    return status_servico('openproject', host, porta)

# -------------------------------------------------------------------------
# 2. GESTÃO DO POOL MULTI-IA
# -------------------------------------------------------------------------
def itens_pool_ia(dados):
    slots_dict = dados.get('ias', {}) if isinstance(dados, dict) else {}
    if isinstance(slots_dict, dict):
        return list(slots_dict.items())
    if isinstance(slots_dict, list):
        return [(it.get('id', str(i)), it) for i, it in enumerate(slots_dict) if isinstance(it, dict)]
    if isinstance(dados, list):
        return [(it.get('id', str(i)), it) for i, it in enumerate(dados) if isinstance(it, dict)]
    return [('principal', dados)]


def resolver_credencial_ia(modelo=None, slot=None):
    cfg_path = garantir_pool_privado_migrado()
    if not os.path.exists(cfg_path):
        return os.getenv('NEWAPI_API_KEY') or os.getenv('NEW_API_KEY') or '', '', False

    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        itens_com_chave = itens_pool_ia(dados)

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
                        return '', '', True

                # Retorna estritamente a chave deste slot (ou vazio se não tiver)
                # NUNCA pega emprestada chave de outro slot com o mesmo modelo!
                for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                    v = slot_encontrado.get(k)
                    if chave_pool_configurada(v):
                        return v, slot_encontrado.get('endpoint') or slot_encontrado.get('url') or '', True
                return '', slot_encontrado.get('endpoint') or slot_encontrado.get('url') or '', True

        # 2. Se NÃO informou slot: busca no pool pelo modelo
        if modelo:
            alvo_m = str(modelo).strip().lower()
            for s_key, it in itens_com_chave:
                if isinstance(it, dict):
                    for campo in ('agent', 'modelo', 'model', 'nome'):
                        if str(it.get(campo) or '').strip().lower() == alvo_m:
                            for k in ('apiKey', 'api_key', 'chave', 'token', 'secret'):
                                v = it.get(k)
                                if chave_pool_configurada(v):
                                    return v, it.get('endpoint') or it.get('url') or '', True

    except Exception as e:
        registrar_falha_operacional('ia_pool_secret_resolution_failed', e)

    return os.getenv('NEWAPI_API_KEY') or os.getenv('NEW_API_KEY') or '', '', False


def resolver_chave_real(modelo=None, slot=None):
    return resolver_credencial_ia(modelo, slot)[0]

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
            dados = request.get_json(force=True, silent=True)
            if not isinstance(dados, dict):
                return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Payload JSON inválido.'}), 400
            try:
                validar_endpoints_payload_pool(dados)
            except PermissionError:
                return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Destino de IA não autorizado.'}), 403
            except ValueError:
                return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Endpoint de IA inválido.'}), 400
            arquivo_original = cfg_path if os.path.exists(cfg_path) else localizar_modelo_pool()
            if os.path.exists(arquivo_original):
                try:
                    with open(arquivo_original, 'r', encoding='utf-8') as f_orig:
                        config_original = json.load(f_orig)
                    dados = mesclar_preservando_segredos(dados, config_original)
                except Exception as e:
                    return resposta_erro_interno(
                        'ia_pool_original_load_failed',
                        e,
                        'Falha ao carregar a configuração anterior do pool.',
                    )
            salvar_pool_privado(cfg_path, dados)
            if arquivo_original == localizar_modelo_pool() and os.path.exists(arquivo_original):
                remover_segredos_modelo_pool(arquivo_original, config_original)
            return jsonify({'sucesso': True, 'status': 'sucesso', 'mensagem': 'Pool salvo com sucesso!'})
        except Exception as e:
            return resposta_erro_interno('ia_pool_save_failed', e, 'Falha ao salvar o pool de IA.')
    try:
        cfg_path = garantir_pool_privado_migrado()
    except Exception as e:
        return resposta_erro_interno('ia_pool_migration_failed', e, 'Falha ao carregar a configuração privada do pool.')
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                pool_raw = json.load(f)
            return jsonify(mascarar_chaves_recursivo(pool_raw))
        except Exception as e:
            return resposta_erro_interno('ia_pool_load_failed', e, 'Falha ao carregar o pool de IA.')
    return jsonify({'status': 'padrao'})

@app.route('/api/v1/ia/testar_slot', methods=['POST'])
def api_v1_ia_testar_slot():
    try:
        t0 = time.time()
        dados = request.get_json(force=True, silent=True)
        if not isinstance(dados, dict):
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Payload JSON inválido.'}), 400
        model = dados.get('model') or dados.get('agent') or 'qwen2.5:14b'
        slot = dados.get('slot', 'ia')
        raw_endpoint = dados.get('endpoint')
        api_key = dados.get('apiKey') or dados.get('api_key') or ''
        if not chave_pool_configurada(api_key):
            api_key, endpoint_pool, credencial_do_pool = resolver_credencial_ia(model, slot)
            if credencial_do_pool:
                if api_key and not endpoint_pool:
                    return jsonify({
                        'sucesso': False,
                        'status': 'erro',
                        'mensagem': 'O slot com credencial configurada não possui endpoint.',
                    }), 400
                raw_endpoint = endpoint_pool or raw_endpoint
            elif api_key:
                raw_endpoint = motor_ia.obter_endpoint_padrao()
        if raw_endpoint is None or raw_endpoint == '':
            raw_endpoint = motor_ia.obter_endpoint_padrao()
        try:
            endpoint = normalizar_endpoint_ia(raw_endpoint)
        except PermissionError:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Destino de IA não autorizado.'}), 403
        except ValueError:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Endpoint de IA inválido.'}), 400

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
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                latencia = int((time.time() - t0) * 1000)
                cod_http = getattr(resp, 'status', 200)
                if not isinstance(cod_http, int):
                    cod_http = 200
                return jsonify({
                    'sucesso': True,
                    'status': 'sucesso',
                    'codigo': cod_http,
                    'codigoHttp': cod_http,
                    'latenciaMs': latencia,
                    'resposta': 'pong'
                }), 200
        except urllib.error.HTTPError as he:
            cod = he.code if he.code in (400, 401, 403, 404, 429) else 502
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': f'Provedor retornou HTTP {he.code}'}), cod
        except TimeoutError:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Timeout ao testar slot de IA.'}), 504
        except urllib.error.URLError as ue:
            registrar_falha_operacional('ia_slot_connection_failed', ue)
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Falha de conexão com o provedor de IA.'}), 502
    except Exception as e:
        return resposta_erro_interno('ia_slot_test_failed', e, 'Falha interna ao testar o slot de IA.')


@app.route('/api/v1/ia/chat', methods=['POST'])
def api_v1_ia_chat():
    try:
        dados = request.get_json(force=True, silent=True)
        if not isinstance(dados, dict):
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Payload JSON inválido.'}), 400
        mensagens = dados.get('mensagens') or dados.get('messages') or []
        ia_alvo = dados.get('ia', 'principal')
        model = dados.get('model', 'qwen2.5:14b' if ia_alvo == 'principal' else 'qwen2.5:7b')
        slot_id = dados.get('slot') or ia_alvo
        raw_endpoint = dados.get('endpoint')
        api_key = dados.get('apiKey') or dados.get('api_key') or ''
        if not chave_pool_configurada(api_key):
            api_key, endpoint_pool, credencial_do_pool = resolver_credencial_ia(model, slot_id)
            if credencial_do_pool:
                if api_key and not endpoint_pool:
                    return jsonify({
                        'sucesso': False,
                        'status': 'erro',
                        'mensagem': 'O slot com credencial configurada não possui endpoint.',
                    }), 400
                raw_endpoint = endpoint_pool or raw_endpoint
            elif api_key:
                raw_endpoint = motor_ia.obter_endpoint_padrao()
        try:
            endpoint = normalizar_endpoint_ia(raw_endpoint)
        except PermissionError:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Destino de IA não autorizado.'}), 403
        except ValueError:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Endpoint de IA inválido.'}), 400

        resultado = motor_ia.executar_chat_ia(
            mensagens=mensagens,
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            temperature=dados.get('temperature', 0.0),
            max_tokens=dados.get('max_tokens', 700),
            timeout=45,
        )
        return jsonify(resultado), resultado.get('codigo', 200)
    except Exception as e:
        return resposta_erro_interno('ia_chat_failed', e, 'Falha interna ao processar a solicitação de IA.')


@app.route('/api/v1/ia/revisar_processo', methods=['POST'])
def api_v1_ia_revisar_processo():
    try:
        dados = request.get_json(force=True, silent=True)
        if not isinstance(dados, dict):
            return jsonify({'sucesso': False, 'erro': 'Payload JSON inválido.'}), 400
        # Rota de revisao usa exclusivamente o endpoint interno configurado no servidor
        model = 'llama3.2:1b'
        api_key, endpoint_pool, credencial_do_pool = resolver_credencial_ia(model, 'revisao')
        if credencial_do_pool and api_key and not endpoint_pool:
            return jsonify({
                'sucesso': False,
                'status': 'erro',
                'mensagem': 'O slot de revisão com credencial configurada não possui endpoint.',
            }), 400
        endpoint = endpoint_pool if credencial_do_pool and endpoint_pool else motor_ia.obter_endpoint_padrao()
        resultado = motor_ia.revisar_processo_ia(
            dados=dados,
            endpoint=endpoint,
            model=model,
            api_key=api_key,
        )
        return jsonify(resultado), resultado.get('codigo', 200)
    except Exception as e:
        return resposta_erro_interno('ia_review_failed', e, 'Falha interna ao revisar o processo.')


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
            'status': 'erro',
            'codigo': 503,
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
        registrar_falha_operacional('openproject_upstream_http_error', he)
        return {
            'sucesso': False,
            'status': 'erro',
            'codigo': 502,
            'upstreamStatus': he.code,
            'card_id': card_id,
            'mensagem': f'OpenProject retornou erro HTTP {he.code}.'
        }
    except TimeoutError as e:
        registrar_falha_operacional('openproject_timeout', e)
        return {
            'sucesso': False,
            'status': 'erro',
            'codigo': 504,
            'card_id': card_id,
            'mensagem': 'Tempo limite ao contatar o OpenProject.'
        }
    except urllib.error.URLError as e:
        timeout = isinstance(getattr(e, 'reason', None), TimeoutError)
        registrar_falha_operacional('openproject_connection_failed', e)
        return {
            'sucesso': False,
            'status': 'erro',
            'codigo': 504 if timeout else 502,
            'card_id': card_id,
            'mensagem': 'Falha de comunicação com o OpenProject.'
        }
    except Exception as e:
        registrar_falha_operacional('openproject_sync_failed', e)
        return {
            'sucesso': False,
            'status': 'erro',
            'codigo': 502,
            'card_id': card_id,
            'mensagem': 'Falha ao sincronizar com o OpenProject.'
        }

@app.route('/api/v1/openproject/sync_card', methods=['POST'])
def api_v1_op_sync_card():
    try:
        dados = request.get_json(force=True, silent=True)
        if not isinstance(dados, dict):
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Payload JSON inválido.'}), 400
        # Aceita tanto card_id quanto cardId (compatibilidade UI)
        card_id = dados.get('card_id') or dados.get('cardId')
        if not card_id:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'card_id ou cardId obrigatório'}), 400
        card_id = str(card_id).strip()
        if not card_id.isdigit() or int(card_id) < 1:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'card_id deve ser um inteiro positivo.'}), 400
        comentario = dados.get('comentario', '')
        descricao = dados.get('descricao', None)
        if not isinstance(comentario, str) or (descricao is not None and not isinstance(descricao, str)):
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'comentario e descricao devem ser strings.'}), 400
        resultado = sincronizar_card_openproject_real(card_id, comentario=comentario, descricao=descricao)
        codigo_http = resultado.get('codigo', 200 if resultado.get('sucesso') else 502)
        return jsonify(resultado), codigo_http
    except Exception as e:
        return resposta_erro_interno('openproject_sync_request_failed', e, 'Falha interna ao sincronizar o cartão.')

@app.route('/api/v1/openproject/sync_batch', methods=['POST'])
def api_v1_op_sync_batch():
    dados = request.get_json(force=True, silent=True)
    if not isinstance(dados, dict):
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Payload JSON inválido.'}), 400
    if 'itens' in dados:
        itens = dados['itens']
    elif 'cards' in dados:
        itens = dados['cards']
    else:
        itens = []
    if not isinstance(itens, list) or any(not isinstance(item, dict) for item in itens):
        return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'itens deve ser uma lista de objetos.'}), 400
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
                registrar_falha_operacional('openproject_batch_item_failed', e)
                processados.append({
                    'card_id': c_id,
                    'sucesso': False,
                    'status': 'erro_conexao',
                    'mensagem': 'Falha ao sincronizar este item com o OpenProject.',
                })

    todos_sucesso = all(p.get('sucesso', False) for p in processados) if processados else True
    return jsonify({
        'sucesso': todos_sucesso,
        'total_processado': len(processados),
        'itens': processados
    }), (200 if todos_sucesso else 502)


@app.route('/api/v1/openproject/historico_agendado_v2', methods=['GET'])
@app.route('/api/v1/openproject/historico_agendado', methods=['GET'])
def api_v1_op_historico():
    for c in ['registro_execucao_agendada.json', 'data/registro_execucao_agendada.json']:
        if os.path.exists(c):
            try:
                with open(c, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
                if isinstance(historico, list):
                    return jsonify({'sucesso': True, 'historico': historico}), 200
                if isinstance(historico, dict) and isinstance(historico.get('historico'), list):
                    return jsonify(historico), 200
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'O histórico de execução possui formato inválido.',
                }), 500
            except (OSError, json.JSONDecodeError) as erro:
                return resposta_erro_interno(
                    'openproject_history_read_failed',
                    erro,
                    'Não foi possível carregar o histórico de execução.',
                )
    return jsonify({
        'sucesso': False,
        'historico': [],
        'mensagem': 'Ainda não há histórico de execução registrado.',
    }), 200


@app.route('/api/v1/processos', methods=['GET'])
def api_v1_processos():
    caminho = os.getenv(
        'COCKPIT_PROCESSOS_FILE',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'processos.json'),
    )
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            processos = json.load(arquivo)
    except FileNotFoundError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Acervo SEI não configurado neste ambiente.',
        }), 503
    except (OSError, json.JSONDecodeError) as erro:
        return resposta_erro_interno(
            'sei_processos_file_read_failed',
            erro,
            'Não foi possível carregar o acervo SEI.',
        )
    if not isinstance(processos, list):
        return jsonify({
            'sucesso': False,
            'mensagem': 'O acervo SEI possui formato inválido.',
        }), 500
    return jsonify({
        'sucesso': True,
        'total': len(processos),
        'processos': processos,
    }), 200

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
            registrar_falha_operacional('glpi_tickets_connection_failed', e)
            return jsonify({
                'sucesso': False,
                'status': 'erro_conexao',
                'mensagem': 'Falha de comunicação com o GLPI.',
                'tickets': [],
            }), 502

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
                return resposta_erro_interno('documentation_load_failed', e, 'Falha ao carregar o documento.')

    return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': 'Arquivo não localizado em disco'}), 404

# -------------------------------------------------------------------------
# 5. MOTOR DE BUSCA E AUTOMAÇÃO SEI 4.1.5 (SA-GTI 110050725)
# -------------------------------------------------------------------------
from motor_sei import MotorSEI
import motor_ia
motor_sei_instance = MotorSEI()

@app.route('/api/v1/sei/status', methods=['GET'])
def api_v1_sei_status():
    status = motor_sei_instance.validar_sessao()
    cod = status.get('codigo') if isinstance(status, dict) else None
    status_publico = {
        campo: status[campo]
        for campo in ('sucesso', 'codigo', 'ativa', 'sessao_ativa', 'autenticado', 'rollback_pendente', 'unidade')
        if isinstance(status, dict) and campo in status
    }
    if isinstance(status, dict) and not status.get('sucesso'):
        status_publico['erro'] = (
            'Sessão do SEI bloqueada por pendência de integridade.'
            if status.get('rollback_pendente')
            else 'Sessão do SEI indisponível.'
        )
    if cod == 503 or (isinstance(status, dict) and status.get('rollback_pendente')):
        return jsonify(status_publico), 503
    return jsonify(status_publico), 200

@app.route('/api/v1/sei/sessao', methods=['POST'])
@requer_autenticacao
def api_v1_sei_salvar_sessao():
    dados = request.get_json(force=True) or {}
    cookies = dados.get('cookies') or dados
    if isinstance(cookies, dict):
        try:
            motor_sei_instance.salvar_sessao(cookies)
            return jsonify({'sucesso': True, 'mensagem': 'Cookies de sessão do SEI atualizados com sucesso.'}), 200
        except Exception as e:
            return resposta_erro_interno('sei_session_save_failed', e, 'Falha ao persistir a sessão do SEI.')
    return jsonify({'sucesso': False, 'mensagem': 'Formato de cookies inválido.'}), 400


@app.route('/api/v1/sei/processos', methods=['GET'])
@requer_autenticacao
def api_v1_sei_processos():
    resultado = motor_sei_instance.listar_caixa_unidade()
    if resultado.get('sucesso'):
        return jsonify(resultado), 200
    cod = resultado.get('codigo')
    erro = str(resultado.get('erro', '')).lower()
    if cod in (400, 404, 429, 503):
        return resposta_erro_sei(resultado, cod)
    if cod == 403 and not resultado.get('sessao_expirada'):
        return resposta_erro_sei(resultado, 403)
    if (cod and cod >= 500) or 'conexão' in erro or 'timeout' in erro or 'falha de conexão' in erro or (cod in (200, 302) and not resultado.get('sessao_expirada')):
        return resposta_erro_sei(resultado, 502)
    if resultado.get('sessao_expirada') or cod == 401:
        return resposta_erro_sei(resultado, 401)
    return resposta_erro_sei(resultado, cod or 502)


def resposta_erro_sei(resultado, codigo):
    if resultado.get('rollback_pendente'):
        mensagem = 'Sessão do SEI bloqueada por pendência de integridade.'
    elif resultado.get('sessao_expirada') or codigo == 401:
        mensagem = 'Sessão do SEI inválida ou expirada.'
    elif codigo == 403:
        mensagem = 'Acesso negado pelo SEI.'
    elif codigo == 504:
        mensagem = 'Tempo limite ao consultar o SEI.'
    else:
        mensagem = 'Falha ao consultar o SEI.'
    resposta = {'sucesso': False, 'codigo': codigo, 'erro': mensagem}
    for campo in ('sessao_expirada', 'rollback_pendente'):
        if campo in resultado:
            resposta[campo] = resultado[campo]
    return jsonify(resposta), codigo

@app.route('/api/v1/sei/buscar', methods=['POST'])
@requer_autenticacao
def api_v1_sei_buscar():
    dados = request.get_json(force=True) or {}
    termo = dados.get('termo') or dados.get('query') or ''
    resultado = motor_sei_instance.buscar_processos(termo=termo)
    if resultado.get('sucesso'):
        return jsonify(resultado), 200
    cod = resultado.get('codigo')
    erro = str(resultado.get('erro', '')).lower()
    if cod in (400, 404, 429, 503):
        return resposta_erro_sei(resultado, cod)
    if cod == 403 and not resultado.get('sessao_expirada'):
        return resposta_erro_sei(resultado, 403)
    if (cod and cod >= 500) or 'conexão' in erro or 'timeout' in erro or 'falha de conexão' in erro or (cod in (200, 302) and not resultado.get('sessao_expirada')):
        return resposta_erro_sei(resultado, 502)
    if resultado.get('sessao_expirada') or cod == 401:
        return resposta_erro_sei(resultado, 401)
    return resposta_erro_sei(resultado, cod or 502)

if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)