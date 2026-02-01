import pandas as pd
from scripts.config import logger, PROCESSED_DIR

INPUT = PROCESSED_DIR / "consolidado_despesas.csv"


def resumo_processado():
    logger.info("Resumo final dos dados processados")

    df = pd.read_csv(INPUT, sep=";", low_memory=False)

    logger.info(f"Total de registros: {len(df):,}")
    logger.info(f"Registros ANS únicos: {df['RegistroANS'].nunique():,}")
    logger.info(f"Anos processados: {sorted(df['Ano'].unique().tolist())}")
    logger.info(
        f"Trimestres processados: {sorted(df['Trimestre'].unique().tolist())}"
    )
    logger.info(
        f"Valor total das despesas: {df['ValorDespesas'].sum():,.2f}"
    )
