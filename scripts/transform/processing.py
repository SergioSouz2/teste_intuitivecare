import pandas as pd
from scripts.config import logger, EXTRACT_DIR, PROCESSED_DIR
from scripts.utils.date_utils import extract_year_quarter
OUTPUT_FILE = PROCESSED_DIR / "despesas_normalizadas.csv"

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.astype(str).str.strip().str.upper().str.replace(" ", "_")
    return df

def clean_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()

def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(".", "").str.replace(",", "."), errors="coerce")

def clean_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)

def find_description_column(df):
    for col in df.columns:
        if any(k in col for k in ["DESCRICAO", "DS_CONTA", "NOME_CONTA"]):
            return col
    return None

def find_value_column(df):
    for col in df.columns:
        if any(k in col for k in ["VALOR", "VL_", "SALDO"]):
            return col
    return None

def find_date_column(df):
    for col in df.columns:
        if "DATA" in col:
            return col
    return None

def is_despesa(text: str) -> bool:
    text = str(text).upper()
    return any(k in text for k in ["DESPESA", "EVENTO", "SINISTRO"])

def process():
    logger.info("Processamento iniciado")
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
    total_rows = 0
    for file in EXTRACT_DIR.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in [".csv", ".txt", ".xlsx"]:
            continue
        try:
            if file.suffix == ".xlsx":
                chunks = [pd.read_excel(file)]
            else:
                chunks = pd.read_csv(file, sep=";", encoding="latin1", chunksize=100_000, low_memory=False)
        except Exception as e:
            logger.error(f"Erro ao ler {file.name}: {e}")
            continue
        for chunk in chunks:
            chunk = normalize_columns(chunk)
            desc_col = find_description_column(chunk)
            value_col = find_value_column(chunk)
            date_col = find_date_column(chunk)
            if not desc_col or not value_col:
                continue
            chunk = chunk[chunk[desc_col].apply(is_despesa)]
            if chunk.empty:
                continue
            chunk["DESCRICAO"] = clean_text(chunk[desc_col])
            chunk["VALOR"] = clean_numeric(chunk[value_col])
            if date_col:
                chunk["DATA"] = clean_date(chunk[date_col])
            else:
                chunk["DATA"] = pd.NaT
            final_chunk = pd.DataFrame({
                "CNPJ": clean_text(chunk.get("REG_ANS")),
                "RazaoSocial": chunk["DESCRICAO"],
                "Ano": None,
                "Trimestre": None,
                "ValorDespesas": chunk["VALOR"],
                "FilePath": str(file)
            })
            ano, trimestre = extract_year_quarter(file, chunk)
            final_chunk["Ano"] = final_chunk["Ano"].fillna(ano)
            final_chunk["Trimestre"] = final_chunk["Trimestre"].fillna(trimestre)
            final_chunk = final_chunk.dropna(subset=["CNPJ", "ValorDespesas"])
            final_chunk.to_csv(OUTPUT_FILE, mode="a", index=False, header=not OUTPUT_FILE.exists(), sep=";", encoding="utf-8")
            total_rows += len(final_chunk)
    logger.info(f"Processamento concluído: {total_rows:,} registros")
