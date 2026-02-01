# import_consolidadas.py
from pathlib import Path
import csv
import logging
from utils import safe_float, safe_int

logger = logging.getLogger(__name__)

def import_despesas_consolidadas(conn, data_dir):
    csv_path = Path(data_dir) / "consolidado_despesas.csv"
    if not csv_path.exists():
        logger.warning(f"Arquivo não encontrado: {csv_path}")
        return

    inserted = 0
    pendentes = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                registro_ans = safe_int(row.get("RegistroANS"))
                ano = safe_int(row.get("Ano"))
                trimestre = safe_int(row.get("Trimestre"))
                valor_despesas = safe_float(row.get("ValorDespesas"))

                cur = conn.cursor()
                cur.execute("SELECT id FROM operadoras WHERE registro_operadora = %s", (registro_ans,))
                result = cur.fetchone()
                if result:
                    operadora_id = result[0]
                    cur.execute(
                        """
                        INSERT INTO despesas_consolidadas(
                            operadora_id, registro_ans, ano, trimestre, valor_despesas
                        ) VALUES (%s, %s, %s, %s, %s)
                        """,
                        (operadora_id, registro_ans, ano, trimestre, valor_despesas)
                    )
                    inserted += 1
                else:
                    cur.execute(
                        """
                        INSERT INTO despesas_consolidadas_pendentes(
                            registro_ans, ano, trimestre, valor_despesas
                        ) VALUES (%s, %s, %s, %s)
                        """,
                        (registro_ans, ano, trimestre, valor_despesas)
                    )
                    pendentes += 1

                conn.commit()
                cur.close()
            except Exception as e:
                logger.error(f"Erro ao importar linha {row}: {e}")
                conn.rollback()
                continue

    logger.info(f"Despesas consolidadas: {inserted}, pendentes: {pendentes}")
