from scripts.config import logger
from scripts.etapa1.extract.download import download_and_extract
from scripts.etapa1.transform.processing import process
from scripts.etapa1.consolidate.consolidation import consolidate
from scripts.etapa1.analysis.resumo_processado import resumo_processado

def main():
    logger.info("PIPELINE INICIADO")
    download_and_extract()
    process()
    consolidate()
    resumo_processado()
    logger.info("PIPELINE FINALIZADO COM SUCESSO")

if __name__ == "__main__":
    main()
