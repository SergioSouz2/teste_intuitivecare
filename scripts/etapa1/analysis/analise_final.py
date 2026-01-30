from scripts.config import logger

# ETAPAS DO PIPELINE
from scripts.download.download_and_extract import download_and_extract
from scripts.inspect.inspect_extracted_files import inspect_extracted_files
from scripts.transform.process_incremental import process_incremental
from scripts.consolidate.consolidate_despesas import consolidate_despesas
from scripts.analysis.analise_final import analise_final


def main():
    logger.info("PIPELINE INICIADO")

    # 1️⃣ Download + Extração
    logger.info("ETAPA 1 - Download e extração dos arquivos")
    download_and_extract()

    # 2️⃣ Inspeção dos arquivos extraídos
    logger.info("ETAPA 2 - Inspeção dos arquivos extraídos")
    inspect_extracted_files()

    # 3️⃣ Transformação / Processamento incremental
    logger.info("ETAPA 3 - Processamento incremental")
    process_incremental()

    # 4️⃣ Consolidação
    logger.info("ETAPA 4 - Consolidação dos dados")
    consolidate_despesas()

    # 5️⃣ Análise final
    logger.info("ETAPA 5 - Análise final dos dados processados")
    analise_final()

    logger.info("PIPELINE FINALIZADO COM SUCESSO")


if __name__ == "__main__":
    main()
