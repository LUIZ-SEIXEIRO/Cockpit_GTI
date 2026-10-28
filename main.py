import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory
from database_mariadb import testar_conexao_mariadb

# Adiciona pasta backend ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from ia import processar_com_failover

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    return send_file(os.path.join(FRONTEND_DIR, 'painel.html'))

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/api/v1/healthcheck', methods=['GET'])
def healthcheck():
    db_conectado = testar_conexao_mariadb()
    return jsonify({
        "status": "online",
        "mariadb": "connected" if db_conectado else "disconnected",
        "timestamp": datetime.now().isoformat(),
        "versao": "1.0.0"
    })

@app.route('/api/v1/ia/processar', methods=['POST'])
def rota_processar_ia():
    dados = request.get_json() or {}
    prompt = dados.get('prompt', '')
    contexto = dados.get('contexto', '')
    nivel = int(dados.get('nivel_preferencial', 1))
    
    if not prompt:
        return jsonify({"erro": "O campo 'prompt' é obrigatório"}), 400
        
    resultado = processar_com_failover(prompt, contexto, nivel_preferencial=nivel)
    return jsonify(resultado)

if __name__ == '__main__':
    print("Iniciando Cockpit GTI em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)