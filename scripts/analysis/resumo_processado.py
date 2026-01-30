import pandas as pd
from scripts.config import logger, PROCESSED_DIR

def resumo_processado():
    file = PROCESSED_DIR / "consolidado_despesas.csv"
    
    df = pd.read_csv(file, sep=";")
    df.columns = df.columns.str.strip().str.upper()  # padroniza
    
    logger.info("Resumo final dos dados processados")
    logger.info(f"Total de registros: {len(df):,}")
    
    if "CNPJ" in df.columns:
        logger.info(f"CNPJs únicos: {df['CNPJ'].nunique():,}")
    else:
        logger.warning("Coluna CNPJ não encontrada!")

    if "VALORDESPESAS" in df.columns:
        logger.info(f"Valor total: {df['VALORDESPESAS'].sum():,.2f}")
    else:
        logger.warning("Coluna VALORDESPESAS não encontrada!")
