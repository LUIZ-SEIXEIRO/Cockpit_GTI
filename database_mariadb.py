import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

DB_USER = os.getenv('DB_USER', 'glpi')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'glpi')
DB_NAME = os.getenv('DB_NAME', 'glpidb')
DB_HOST = '127.0.0.1'
DB_PORT = int(os.getenv('DB_PORT', 3306))

def testar_conexao_mariadb() -> bool:
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        conn.close()
        return True
    except Exception as err:
        print(f"Erro no MariaDB: {err}")
        return False