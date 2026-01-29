from dotenv import load_dotenv
import os

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Tuple
import logging

# ======================
# ENV
# ======================
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise RuntimeError("Variável BASE_URL não encontrada no arquivo .env")

# ======================
# PATHS
# ======================
DEST_DIR = Path("data/raw")
LOG_DIR = Path("logs")

DEST_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ======================
# LOGGING
# ======================
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def find_demonstracoes_contabeis_url(base_url: str) -> str:
    """
    Localiza a URL da pasta 'demonstrações_contabeis' na URL base.
    """
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar URL base: {e}")
        raise RuntimeError(f"Erro ao acessar URL base: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if "demonstra" in href:
            demo_url = (
                href
                if href.startswith("http")
                else base_url.rstrip("/") + "/" + href.lstrip("/")
            )
            logger.info(f"Pasta encontrada: {demo_url}")
            return demo_url

    logger.error("Pasta 'demonstrações_contabeis' não encontrada")
    raise RuntimeError("Pasta 'demonstrações_contabeis' não encontrada")


def download_files(trimesters: List[Tuple[str, str]], dest_dir: Path) -> None:
    """
    Baixa os arquivos dos trimestres especificados.
    """
    for filename, file_url in trimesters:
        filepath = dest_dir / filename

        try:
            logger.info(f"Baixando: {filename}")
            response = requests.get(file_url, timeout=30, stream=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"✓ Arquivo salvo: {filepath}")

        except requests.RequestException as e:
            logger.error(f"Erro ao baixar {filename}: {e}")
        except IOError as e:
            logger.error(f"Erro ao salvar {filename}: {e}")


def get_last_trimesters(base_url: str, limit: int = 3) -> List[Tuple[str, str]]:
    """
    Obtém os últimos trimestres mais recentes.
    """
    all_trimesters: List[Tuple[str, str, int, int]] = []

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar URL: {e}")
        raise RuntimeError(f"Erro ao acessar URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    years = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip("/").strip()
        if href.isdigit() and 1900 <= int(href) <= 2100:
            years.append(int(href))

    years.sort(reverse=True)

    for year in years:
        year_url = f"{base_url.rstrip('/')}/{year}/"

        try:
            r = requests.get(year_url, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Erro ao acessar {year_url}: {e}")
            continue

        s = BeautifulSoup(r.text, "html.parser")

        for a in s.find_all("a", href=True):
            href = a["href"].strip()
            if href.endswith(".zip") and "T" in href and href[0].isdigit():
                try:
                    quarter = int(href[0])
                    file_year = int(href.split("T")[1].replace(".zip", ""))
                    if 1 <= quarter <= 4:
                        file_url = f"{year_url.rstrip('/')}/{href}"
                        all_trimesters.append(
                            (href, file_url, file_year, quarter)
                        )
                except (ValueError, IndexError):
                    pass

    all_trimesters.sort(key=lambda x: (x[2], x[3]), reverse=True)

    return [(t[0], t[1]) for t in all_trimesters[:limit]]


def main() -> int:
    """
    Função principal.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO DOWNLOAD DE DEMONSTRAÇÕES CONTÁBEIS")
    logger.info("=" * 60)

    try:
        demo_url = find_demonstracoes_contabeis_url(BASE_URL)
        last_trimesters = get_last_trimesters(demo_url)

        if not last_trimesters:
            logger.warning("Nenhum arquivo encontrado para download")
            return 0

        logger.info(f"Iniciando download de {len(last_trimesters)} arquivo(s)")
        download_files(last_trimesters, DEST_DIR)

        logger.info("✓ Download concluído com sucesso!")

        logger.info("Resumo final:")
        for filename, _ in last_trimesters:
            logger.info(f"  ✓ {filename}")

        return 0

    except RuntimeError as e:
        logger.error(f"Erro durante a execução: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
