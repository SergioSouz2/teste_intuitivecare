# import_agregadas.py
from pathlib import Path
import csv
import logging
from utils import safe_float, sanitize_value

logger = logging.getLogger(__name__)


def is_valid_row(razao_social, total_despesas, media_despesas):
    """Valida se a linha tem dados mínimos para inserir na tabela principal"""
    if not razao_social:
        return False
    if total_despesas is None or media_despesas is None:
        return False
    return True


def import_despesas_agregadas(conn, data_dir):
    csv_path = Path(data_dir) / "despesas_agregadas.csv"
    if not csv_path.exists():
        logger.warning(f"Arquivo não encontrado: {csv_path}")
        return

    inserted = 0
    pendentes = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                # 🔧 CORREÇÃO AQUI (max_len adicionado)
                razao_social = sanitize_value(row.get("RAZAO_SOCIAL"), 255)
                uf = sanitize_value(row.get("UF"), 20)

                if uf == "INVÁLIDO" or uf == "":
                    uf = None

                total_despesas = safe_float(row.get("total_despesas"))
                media_despesas = safe_float(row.get("media_despesas"))
                desvio_padrao = safe_float(row.get("desvio_padrao"))

                cur = conn.cursor()

                if is_valid_row(razao_social, total_despesas, media_despesas):
                    # tenta buscar a operadora
                    cur.execute(
                        """
                        SELECT id
                        FROM operadoras
                        WHERE razao_social = %s
                          AND uf IS NOT DISTINCT FROM %s
                        """,
                        (razao_social, uf)
                    )
                    result = cur.fetchone()

                    if result:
                        operadora_id = result[0]
                        # inserir na tabela principal
                        cur.execute(
                            """
                            INSERT INTO despesas_agregadas(
                                operadora_id, razao_social, uf,
                                total_despesas, media_despesas, desvio_padrao
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                operadora_id,
                                razao_social,
                                uf,
                                total_despesas,
                                media_despesas,
                                desvio_padrao
                            )
                        )
                        inserted += 1
                    else:
                        # operadora não encontrada → pendentes
                        cur.execute(
                            """
                            INSERT INTO despesas_agregadas_pendentes(
                                razao_social, uf,
                                total_despesas, media_despesas, desvio_padrao
                            ) VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                razao_social,
                                uf,
                                total_despesas,
                                media_despesas,
                                desvio_padrao
                            )
                        )
                        pendentes += 1
                else:
                    # linha inválida → pendentes
                    cur.execute(
                        """
                        INSERT INTO despesas_agregadas_pendentes(
                            razao_social, uf,
                            total_despesas, media_despesas, desvio_padrao
                        ) VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            razao_social,
                            uf,
                            total_despesas,
                            media_despesas,
                            desvio_padrao
                        )
                    )
                    pendentes += 1

                conn.commit()
                cur.close()

            except Exception as e:
                logger.error(f"Erro ao importar linha {row}: {e}")
                conn.rollback()
                continue

    logger.info(f"Despesas agregadas: {inserted}, pendentes: {pendentes}")
