from scripts.config import logger, EXTRACT_DIR
import pandas as pd


def inspect_extracted():
    logger.info("Etapa 2 - Inspeção dos arquivos extraídos")

    csvs = sorted(EXTRACT_DIR.rglob("*.csv"))

    if not csvs:
        logger.warning("Nenhum CSV encontrado em data/extracted")
        return

    logger.info(f"{len(csvs)} arquivo(s) CSV encontrados")

    for path in csvs:
        try:
            df = pd.read_csv(path, sep=";", encoding="latin1")
            logger.info(
                f"Arquivo: {path.name} | "
                f"Trimestre: {path.parent.name} | "
                f"Linhas: {len(df):,} | "
                f"Colunas: {len(df.columns)}"
            )
        except Exception as e:
            logger.error(f"Erro ao ler {path.name}: {e}")
