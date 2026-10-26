import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Uso local: carrega o .env da raiz sem sobrescrever variaveis ja injetadas
# (no Docker, o docker-compose.yml injeta as variaveis).
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"A variavel de ambiente {name} e obrigatoria.")
    return value


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=_required("DB_USER"),
    password=_required("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "db"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=_required("DB_NAME"),
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def check_database_connection() -> None:
    """Executa um SELECT 1; levanta excecao se o banco estiver inacessivel."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
