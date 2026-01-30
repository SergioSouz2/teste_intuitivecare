import pandas as pd
from scripts.config import logger, EXTRACT_DIR, PROCESSED_DIR
from scripts.utils.date_utils import extract_year_quarter

OUTPUT_FILE = PROCESSED_DIR / "despesas_normalizadas.csv"

# ---------- Funções auxiliares ----------
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

# ---------- Filtro específico ----------
def is_eventos_sinistros(text: str) -> bool:
    if not isinstance(text, str):
        return False
    text_normalized = text.upper().replace(" ", "").replace("-", "").replace("/", "")
    return "EVENTOSSINISTROS" in text_normalized

# ---------- Função principal ----------
def process():
    logger.info("Processamento iniciado")
    
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
    
    total_rows = 0
    suspeitas_valor = 0
    suspeitas_data = 0
    all_chunks = []

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

            # Filtro "EVENTOS/SINISTROS"
            chunk = chunk[chunk[desc_col].apply(is_eventos_sinistros)]
            if chunk.empty:
                continue
            
            # Limpeza
            chunk["DESCRICAO"] = clean_text(chunk[desc_col])
            chunk["VALOR"] = clean_numeric(chunk[value_col])
            if date_col:
                chunk["DATA"] = clean_date(chunk[date_col])
            else:
                chunk["DATA"] = pd.NaT

            # Remove linhas sem CNPJ
            chunk["REG_ANS"] = clean_text(chunk.get("REG_ANS"))
            chunk = chunk.dropna(subset=["REG_ANS"])

            # Remove valores zerados ou negativos
            mask_valor_suspeito = chunk["VALOR"] <= 0
            if mask_valor_suspeito.any():
                suspeitas_valor += mask_valor_suspeito.sum()
                logger.warning(f"{mask_valor_suspeito.sum()} linhas com VALOR <= 0 em {file.name}")
            chunk = chunk[chunk["VALOR"] > 0]

            # Log linhas com datas inválidas
            if date_col:
                mask_data_suspeita = chunk["DATA"].isna()
                if mask_data_suspeita.any():
                    suspeitas_data += mask_data_suspeita.sum()
                    logger.warning(f"{mask_data_suspeita.sum()} linhas com DATA inválida em {file.name}")
            
            # Monta DataFrame final
            final_chunk = pd.DataFrame({
                "CNPJ": chunk["REG_ANS"],
                "RazaoSocial": chunk["DESCRICAO"],
                "Ano": None,
                "Trimestre": None,
                "ValorDespesas": chunk["VALOR"],
                "FilePath": str(file)
            })
            
            # Extrai Ano e Trimestre
            ano, trimestre = extract_year_quarter(file, chunk)
            final_chunk["Ano"] = final_chunk["Ano"].fillna(ano)
            final_chunk["Trimestre"] = final_chunk["Trimestre"].fillna(trimestre)
            
            all_chunks.append(final_chunk)
            total_rows += len(final_chunk)

    # ---------- Consolidação e padronização de CNPJs ----------
    if all_chunks:
        df_consolidado = pd.concat(all_chunks, ignore_index=True)

        # Padroniza RazaoSocial: para CNPJs duplicados, mantém a primeira RazaoSocial não vazia
        df_consolidado["RazaoSocial"] = df_consolidado.groupby("CNPJ")["RazaoSocial"].transform(
            lambda x: x.ffill().bfill().iloc[0]
        )

        # Remove duplicados exatos (CNPJ + Ano + Trimestre + Valor)
        df_consolidado = df_consolidado.drop_duplicates(subset=["CNPJ", "Ano", "Trimestre", "ValorDespesas"])

        # Salva CSV final
        df_consolidado.to_csv(
            OUTPUT_FILE,
            index=False,
            sep=";",
            encoding="utf-8"
        )
        logger.info(f"Arquivo gerado: {OUTPUT_FILE}")
    else:
        logger.warning("Nenhum registro encontrado para gerar CSV.")

    logger.info(f"Processamento concluído: {total_rows:,} registros")
    logger.info(f"Linhas com VALOR suspeito removidas: {suspeitas_valor}")
    logger.info(f"Linhas com DATA suspeita: {suspeitas_data}")
