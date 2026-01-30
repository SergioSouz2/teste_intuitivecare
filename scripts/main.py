from scripts.config import logger
from scripts.extract.download import download_and_extract
from scripts.transform.processing import process
from scripts.consolidate.consolidation import consolidate
from scripts.analysis.resumo_processado import resumo_processado

def main():
    logger.info("PIPELINE INICIADO")
    download_and_extract()
    process()
    consolidate()
    resumo_processado()
    logger.info("PIPELINE FINALIZADO COM SUCESSO")

if __name__ == "__main__":
    main()
