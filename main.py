import os
from datetime import datetime
from flask import Flask, jsonify, send_file, send_from_directory
from database_mariadb import testar_conexao_mariadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    """Serve a casca principal da SPA (painel.html)."""
    return send_file(os.path.join(FRONTEND_DIR, 'painel.html'))

@app.route('/<path:path>')
def static_files(path):
    """Entrega automaticamente scripts, css, abas e imagens da pasta frontend."""
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

if __name__ == '__main__':
    print("Iniciando Cockpit GTI em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)