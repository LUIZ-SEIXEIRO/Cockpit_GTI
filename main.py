# main.py
import os
from flask import Flask, jsonify
from database_mariadb import connect_to_mariadb

# Configurações do .env
API_KEY = os.getenv('API_KEY')
GLPI_TOKEN = os.getenv('GLPI_TOKEN')
OPENPROJECT_API_KEY = os.getenv('OPENPROJECT_API_KEY')

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

app = Flask(__name__)

@app.route('/healthcheck')
def healthcheck():
    try:
        conn = connect_to_mariadb()
        if conn:
            conn.close()
            return jsonify({"status": "healthy", "database": "connected"}), 200
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 500
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
