import pandas as pd

def run_query(conn):
    """
    Retorna as 5 operadoras com maior crescimento percentual de despesas
    entre o primeiro e o último trimestre analisado.
    """
    sql = """
    WITH totais_trimestre AS (
        SELECT
            dc.operadora_id,
            dc.ano,
            dc.trimestre,
            SUM(dc.valor_despesas) AS total_trimestre,
            (dc.ano * 10 + dc.trimestre) AS periodo
        FROM despesas_consolidadas dc
        GROUP BY dc.operadora_id, dc.ano, dc.trimestre
    ),
    min_max AS (
        SELECT
            operadora_id,
            MIN(periodo) AS min_periodo,
            MAX(periodo) AS max_periodo
        FROM totais_trimestre
        GROUP BY operadora_id
    ),
    valores AS (
        SELECT
            t.operadora_id,
            MAX(CASE WHEN t.periodo = m.min_periodo THEN t.total_trimestre END) AS valor_inicio,
            MAX(CASE WHEN t.periodo = m.max_periodo THEN t.total_trimestre END) AS valor_fim
        FROM totais_trimestre t
        JOIN min_max m ON t.operadora_id = m.operadora_id
        GROUP BY t.operadora_id
    )
    SELECT
        o.razao_social,
        ROUND(
            ((v.valor_fim - v.valor_inicio) / v.valor_inicio) * 100,
            2
        ) AS crescimento_percentual
    FROM valores v
    JOIN operadoras o ON o.id = v.operadora_id
    WHERE v.valor_inicio > 0
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """

    df = pd.read_sql(sql, conn)

    print("\n=== 5 Operadoras com maior crescimento percentual ===")
    print(df)
