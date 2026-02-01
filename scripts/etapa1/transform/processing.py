import pandas as pd
from scripts.config import logger, EXTRACT_DIR, PROCESSED_DIR
from scripts.utils.date_utils import extract_year_quarter

OUTPUT_FILE = PROCESSED_DIR / "despesas_normalizadas.csv"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )
    return df


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )


def find_column(df, keywords):
    for col in df.columns:
        if any(k in col for k in keywords):
            return col
    return None


def is_despesa(text: str) -> bool:
    return "EVENTOS/SINISTROS" in str(text).upper()


def process():
    logger.info("Processamento iniciado")

    # 🔑 garante que a pasta existe (caso tenha sido apagada)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_rows = 0

    for file in EXTRACT_DIR.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in [".csv", ".txt", ".xlsx"]:
            continue

        logger.info(f"📂 Lendo arquivo extraído: {file.name}")

        try:
            if file.suffix == ".xlsx":
                chunks = [pd.read_excel(file)]
            else:
                chunks = pd.read_csv(
                    file,
                    sep=";",
                    encoding="latin1",
                    chunksize=100_000,
                    low_memory=False
                )
        except Exception as e:
            logger.error(f"Erro ao ler {file.name}: {e}")
            continue

        for chunk in chunks:
            chunk = normalize_columns(chunk)

            desc_col = find_column(chunk, ["DESCRICAO", "DS_CONTA", "NOME_CONTA"])
            reg_col = find_column(chunk, ["REG_ANS", "REGISTRO"])
            saldo_ini_col = find_column(chunk, ["VL_SALDO_INICIAL"])
            saldo_fim_col = find_column(chunk, ["VL_SALDO_FINAL"])

            if not all([desc_col, reg_col, saldo_ini_col, saldo_fim_col]):
                continue

            # Filtra apenas despesas
            chunk = chunk[chunk[desc_col].apply(is_despesa)]
            if chunk.empty:
                continue

            # Limpeza numérica
            chunk["SALDO_INICIAL"] = clean_numeric(chunk[saldo_ini_col])
            chunk["SALDO_FINAL"] = clean_numeric(chunk[saldo_fim_col])

            # Cálculo da despesa
            chunk["VALOR_DESPESAS"] = chunk["SALDO_FINAL"] - chunk["SALDO_INICIAL"]
            chunk = chunk[chunk["VALOR_DESPESAS"] > 0]

            if chunk.empty:
                continue

            # Ano e trimestre
            ano, trimestre = extract_year_quarter(file, chunk)

            final_chunk = pd.DataFrame({
                "RegistroANS": chunk[reg_col].astype(str).str.zfill(6),
                "Ano": ano,
                "Trimestre": trimestre,
                "ValorDespesas": chunk["VALOR_DESPESAS"]
            })

            final_chunk = final_chunk.dropna(
                subset=["RegistroANS", "ValorDespesas"]
            )

            logger.info(
                f"➡️ Processando {file.name} | Linhas válidas: {len(final_chunk)}"
            )

            final_chunk.to_csv(
                OUTPUT_FILE,
                mode="a",
                index=False,
                header=not OUTPUT_FILE.exists(),
                sep=";",
                encoding="utf-8"
            )

            total_rows += len(final_chunk)

    logger.info(f"Processamento concluído: {total_rows:,} registros")
