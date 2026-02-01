import requests
from scripts.config import RAW_DIR, logger

URL_OPERADORAS = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/"
    "operadoras_de_plano_de_saude_ativas/"
    "Relatorio_cadop.csv"
)

def download_operadoras():
    output_path = RAW_DIR / "operadoras_ativas.csv"

    if output_path.exists():
        logger.info("Arquivo de operadoras já existe. Removendo para novo download.")
        output_path.unlink()

    logger.info("Baixando dados cadastrais das operadoras (ANS)")
    response = requests.get(URL_OPERADORAS, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    logger.info(f"Arquivo salvo em: {output_path}")

    return output_path
