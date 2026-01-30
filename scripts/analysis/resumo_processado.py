from scripts.config import logger, PROCESSED_DIR
import pandas as pd

def resumo_processado():
    logger.info("Resumo final dos dados processados")
    path = PROCESSED_DIR / "consolidado_despesas.csv"
    df = pd.read_csv(path, sep=",", low_memory=False)
    logger.info(f"Total de registros: {len(df):,}")
    logger.info(f"CNPJs únicos: {df['CNPJ'].nunique():,}")
    logger.info(f"Valor total: R$ {df['ValorDespesas'].sum():,.2f}")
