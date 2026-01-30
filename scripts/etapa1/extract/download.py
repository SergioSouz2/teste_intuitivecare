import zipfile
import requests
import re
from bs4 import BeautifulSoup
from typing import List, Tuple
from scripts.config import logger, BASE_URL, RAW_DIR, EXTRACT_DIR

def find_demonstracoes_url() -> str:
    r = requests.get(BASE_URL, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        if "demonstra" in a["href"].lower():
            return BASE_URL.rstrip("/") + "/" + a["href"].lstrip("/")
    raise RuntimeError("Pasta demonstrações não encontrada")

def get_last_trimesters(url: str, limit=3) -> List[Tuple[str, str]]:
    files = []
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    years = sorted(
        [int(a["href"].strip("/")) for a in soup.find_all("a", href=True) if a["href"].strip("/").isdigit()],
        reverse=True
    )
    for year in years:
        y_url = f"{url.rstrip('/')}/{year}/"
        s = BeautifulSoup(requests.get(y_url).text, "html.parser")
        for a in s.find_all("a", href=True):
            if a["href"].endswith(".zip") and a["href"][0].isdigit():
                files.append((a["href"], f"{y_url}{a['href']}"))
    return files[:limit]

def download_and_extract():
    logger.info("Download e extração iniciados")
    base = find_demonstracoes_url()
    files = get_last_trimesters(base)
    for name, url in files:
        zip_path = RAW_DIR / name
        logger.info(f"Baixando {name}")
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        logger.info(f"Extraindo {name}")
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(EXTRACT_DIR / zip_path.stem)
    logger.info("Download e extração concluídos")
