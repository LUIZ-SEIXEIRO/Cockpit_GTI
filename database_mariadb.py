import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

DB_USER = os.getenv('DB_USER', 'glpi')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'glpi')
DB_NAME = os.getenv('DB_NAME', 'glpidb')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))

def testar_conexao_mariadb() -> bool:
    try:
        cnx = mysql.connector.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST,
            port=DB_PORT, database=DB_NAME, connection_timeout=3
        )
        if cnx.is_connected():
            cnx.close()
            return True
        return False
    except Exception as err:
        print(f"Erro no MariaDB: {err}")
        return False