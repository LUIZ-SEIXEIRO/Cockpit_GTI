import os
import mariadb

def connect_to_mariadb():
    """
    Tenta conectar ao banco de dados MariaDB usando variáveis de ambiente.
    Retorna o objeto de conexão se bem-sucedido, None caso contrário.
    """
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    if not all([db_host, db_user, db_password, db_name]):
        print("Erro: Variáveis de ambiente do banco de dados não configuradas.")
        return None

    try:
        conn = mariadb.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return conn
    except mariadb.Error as e:
        print(f"Erro ao conectar ao MariaDB: {e}")
        return None
