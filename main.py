import os
from datetime import datetime
from flask import Flask, jsonify
from database_mariadb import testar_conexao_mariadb

app = Flask(__name__)

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