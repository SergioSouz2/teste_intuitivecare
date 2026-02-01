import pandas as pd
from scripts.config import logger

def agregar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Agregação de despesas iniciada")

    colunas_necessarias = ["RAZAO_SOCIAL", "UF", "ValorDespesas"]
    for c in colunas_necessarias:
        if c not in df.columns:
            raise ValueError(f"Colunas obrigatórias ausentes para agregação: {c}")

    # Agrupar por RazaoSocial e UF
    df_agg = df.groupby(
        ["RAZAO_SOCIAL", "UF"], as_index=False
    ).agg(
        total_despesas=("ValorDespesas", lambda x: x[x != "INVÁLIDO"].sum()),
        media_despesas=("ValorDespesas", lambda x: x[x != "INVÁLIDO"].mean()),
        desvio_padrao=("ValorDespesas", lambda x: x[x != "INVÁLIDO"].std())
    )

    # Ordenar por total_despesas decrescente
    df_agg = df_agg.sort_values("total_despesas", ascending=False)

  

    return df_agg

