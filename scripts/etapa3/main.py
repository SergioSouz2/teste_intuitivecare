import os
from dotenv import load_dotenv
import psycopg2
import logging
from pathlib import Path
from import_csv import import_operadoras

# ---------------------------
# Logging
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
              logging.StreamHandler()]
)

logger = logging.getLogger("pipeline")

# ---------------------------
# Variáveis de ambiente
# ---------------------------
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATA_DIR = os.getenv("DATA_DIR")

# ---------------------------
# Conexão
# ---------------------------
def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Conexão com o banco estabelecida com sucesso.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise

# ---------------------------
# Main
# ---------------------------
def main():
    logger.info("Pipeline Etapa 3 iniciado")
    conn = connect_db()
    try:
        raw_dir = Path(DATA_DIR) / "raw"
        logger.info("Iniciando importação de operadoras")
        import_operadoras.import_operadoras(conn, raw_dir)
        logger.info("Importação de operadoras concluída com sucesso")
        print("Importação de operadoras concluída com sucesso!")
    finally:
        conn.close()
        logger.info("Conexão com o banco encerrada")

if __name__ == "__main__":
    main()
