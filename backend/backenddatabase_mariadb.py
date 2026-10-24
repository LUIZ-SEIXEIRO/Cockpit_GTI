import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

MYSQL_USER = os.getenv("MYSQL_USER", "spaguas_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "spaguas_pass_2026")
# O host deve corresponder ao nome do serviço/contêiner no docker-compose
MYSQL_HOST = os.getenv("MYSQL_HOST", "spaguas-mariadb") 
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "cockpit_spaguas")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Conexão com MariaDB orquestrada com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar no MariaDB: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()