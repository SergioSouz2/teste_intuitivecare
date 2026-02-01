import pandas as pd

def run_query(conn):
    """
    Conta quantas operadoras tiveram despesas acima da média geral
    em pelo menos 2 trimestres analisados.
    """
    sql = """
    WITH totais_trimestre AS (
        SELECT
            operadora_id,
            ano,
            trimestre,
            SUM(valor_despesas) AS total_trimestre
        FROM despesas_consolidadas
        GROUP BY operadora_id, ano, trimestre
    ),
    media_geral AS (
        SELECT AVG(total_trimestre) AS media
        FROM totais_trimestre
    ),
    acima_media AS (
        SELECT
            t.operadora_id,
            CASE
                WHEN t.total_trimestre > m.media THEN 1
                ELSE 0
            END AS acima
        FROM totais_trimestre t
        CROSS JOIN media_geral m
    ),
    contagem AS (
        SELECT
            operadora_id,
            SUM(acima) AS trimestres_acima
        FROM acima_media
        GROUP BY operadora_id
    )
    SELECT COUNT(*) AS qtd_operadoras
    FROM contagem
    WHERE trimestres_acima >= 2;
    """

    df = pd.read_sql(sql, conn)

    print("\n=== Operadoras com despesas acima da média em ≥ 2 trimestres ===")
    print(df)
