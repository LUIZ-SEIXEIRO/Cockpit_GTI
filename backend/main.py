# -*- coding: utf-8 -*-
import os, sys, json, time, socket, urllib.request, urllib.error
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

@app.after_request
def adicionar_cabecalhos_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    return response

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
        endpoint = 'http://100.103.100.98:3001/v1'
    endpoint = endpoint.strip().rstrip('/')
    if 'localhost:3001' in endpoint or '127.0.0.1:3001' in endpoint:
        endpoint = endpoint.replace('localhost:3001', '100.103.100.98:3001').replace('127.0.0.1:3001', '100.103.100.98:3001')
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

@app.route('/api/v1/telemetria', methods=['GET'])
def rota_telemetria():
    def checar_porta(host, porta, timeout=0.8):
        try:
            s = socket.create_connection((host, porta), timeout=timeout)
            s.close()
            return True
        except Exception:
            return False
    return jsonify({
        'mariadb': checar_porta('127.0.0.1', 3306),
        'ollama': checar_porta('127.0.0.1', 11434),
        'glpi': checar_porta('10.199.43.26', 443) or checar_porta('127.0.0.1', 8088),
        'openproject': checar_porta('143.107.108.115', 443) or checar_porta('127.0.0.1', 8090),
        'newapi': checar_porta('100.103.100.98', 3001) or checar_porta('127.0.0.1', 3001)
    })

@app.route('/api/v1/ia/pool', methods=['GET', 'POST'])
def api_v1_ia_pool():
    cfg_path = localizar_config_pool()
    if request.method == 'POST':
        try:
            dados = request.get_json(force=True) or {}
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            return jsonify({'sucesso': True, 'status': 'sucesso', 'mensagem': 'Pool salvo!'})
        except Exception as e:
            return jsonify({'sucesso': False, 'status': 'erro', 'mensagem': str(e)}), 200
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception:
            pass
    return jsonify({'status': 'padrao'})

@app.route('/api/v1/ia/testar_slot', methods=['POST'])
def api_v1_ia_testar_slot():
    try:
        t0 = time.time()
        dados = request.get_json(force=True) or {}
        raw_endpoint = dados.get('endpoint', 'http://100.103.100.98:3001/v1')
        endpoint = normalizar_endpoint_ia(raw_endpoint)
        api_key = dados.get('apiKey', 'sk-RAZNLjgeaKLVgufkyiemxilJb2HZU6ilvkmTpvLXoOwyIaUL')
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
        with urllib.request.urlopen(req, timeout=40) as resp:
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
        mensagens = dados.get('mensagens', [])
        ia_alvo = dados.get('ia', 'principal')
        endpoint = normalizar_endpoint_ia(dados.get('endpoint', 'http://100.103.100.98:3001/v1'))
        api_key = dados.get('apiKey', 'sk-RAZNLjgeaKLVgufkyiemxilJb2HZU6ilvkmTpvLXoOwyIaUL')
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
        with urllib.request.urlopen(req, timeout=30) as resp:
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

@app.route('/api/v1/glpi/tickets', methods=['GET'])
def api_v1_glpi_tickets():
    return jsonify({'origem': 'GLPI 10 Cache', 'total': 15, 'tickets': []})


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
        os.path.join(base, '..', 'docs', arquivo),
        os.path.abspath(os.path.join('docs', arquivo))
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
