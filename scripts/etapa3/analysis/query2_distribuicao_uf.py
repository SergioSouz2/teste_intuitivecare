import pandas as pd

def run_query(conn):
    """
    Mostra:
    1) Os 5 estados com maiores despesas totais
    2) A média de despesas por operadora nesses estados
    """

    # ---------------------------
    # 1) Top 5 UFs por despesas
    # ---------------------------
    sql_total = """
    SELECT
        o.uf,
        SUM(dc.valor_despesas) AS total_despesas
    FROM despesas_consolidadas dc
    JOIN operadoras o ON o.id = dc.operadora_id
    GROUP BY o.uf
    ORDER BY total_despesas DESC
    LIMIT 5;
    """

    # ---------------------------
    # 2) Média por operadora nos Top 5 UFs
    # ---------------------------
    sql_media = """
    WITH top_ufs AS (
        SELECT
            o.uf
        FROM despesas_consolidadas dc
        JOIN operadoras o ON o.id = dc.operadora_id
        GROUP BY o.uf
        ORDER BY SUM(dc.valor_despesas) DESC
        LIMIT 5
    )
    SELECT
        sub.uf,
        AVG(sub.total_operadora) AS media_por_operadora
    FROM (
        SELECT
            o.uf,
            dc.operadora_id,
            SUM(dc.valor_despesas) AS total_operadora
        FROM despesas_consolidadas dc
        JOIN operadoras o ON o.id = dc.operadora_id
        WHERE o.uf IN (SELECT uf FROM top_ufs)
        GROUP BY o.uf, dc.operadora_id
    ) sub
    GROUP BY sub.uf
    ORDER BY media_por_operadora DESC;
    """

    df_total = pd.read_sql(sql_total, conn)
    df_media = pd.read_sql(sql_media, conn)

    print("\n=== Top 5 UFs por despesas totais ===")
    print(df_total)

    print("\n=== Média de despesas por operadora nos Top 5 UFs ===")
    print(df_media)
