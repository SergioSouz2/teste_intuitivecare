from scripts.config import logger
from pathlib import Path
import os
from dotenv import load_dotenv
import psycopg2

from scripts.etapa3.import_csv.import_operadoras import import_operadoras
from scripts.etapa3.import_csv.import_consolidadas import import_despesas_consolidadas
from scripts.etapa3.import_csv.import_agregadas import import_despesas_agregadas

from scripts.etapa3.analysis.query1_crescimento import run_query as query_crescimento
from scripts.etapa3.analysis.query2_distribuicao_uf import run_query as query_ufs
from scripts.etapa3.analysis.query3_acima_media import run_query as query_acima_media




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

raw_dir = Path(DATA_DIR) / "raw"
processed_dir = Path(DATA_DIR) / "processed"

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
# Imports
# ---------------------------
def run_imports(conn):
    logger.info("Iniciando importação de operadoras")
    import_operadoras(conn, raw_dir)
    logger.info("Importação de operadoras concluída")

    logger.info("Iniciando importação de despesas consolidadas")
    import_despesas_consolidadas(conn, processed_dir)
    logger.info("Importação de despesas consolidadas concluída")

    logger.info("Iniciando importação de despesas agregadas")
    import_despesas_agregadas(conn, processed_dir)
    logger.info("Importação de despesas agregadas concluída")

# ---------------------------
# Queries Analíticas
# ---------------------------
def run_analytics(conn):
    logger.info("Executando Query 1 – Crescimento percentual")
    query_crescimento(conn)

    logger.info("Executando Query 2 – Distribuição por UF")
    query_ufs(conn)

    logger.info("Executando Query 3 – Operadoras acima da média")
    query_acima_media(conn)

# ---------------------------
# Main
# ---------------------------
def main():
    logger.info("Pipeline Etapa 3 iniciado")
    conn = connect_db()

    try:
        run_imports(conn)
        run_analytics(conn)
    finally:
        conn.close()
        logger.info("Conexão com o banco encerrada")

if __name__ == "__main__":
    main()
