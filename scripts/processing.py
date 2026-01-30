import pandas as pd
from pathlib import Path
from scripts.config import logger, EXTRACT_DIR, PROCESSED_DIR


OUTPUT_FILE = PROCESSED_DIR / "despesas_normalizadas.csv"


def normalize_columns(df):
    df.columns = df.columns.str.strip().str.upper()
    return df


def is_despesa(descricao: str) -> bool:
    keys = ["DESPESA", "EVENTO", "SINISTRO"]
    return any(k in descricao.upper() for k in keys)


def process():
    logger.info("Processamento incremental iniciado")

    total_rows = 0
    total_files = 0

    def _clean_numeric(series: pd.Series) -> pd.Series:
        """Normaliza valores numéricos: remove separador de milhares e converte vírgula para ponto."""
        return pd.to_numeric(
            series.astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        )

    for file in EXTRACT_DIR.rglob("*"):
        if not file.is_file():
            continue

        file_suffix = file.suffix.lower()
        
        # Validar formato suportado
        if file_suffix not in [".csv", ".txt", ".xlsx"]:
            continue
        
        logger.info(f"Processando arquivo: {file.name} (formato: {file_suffix})")
        total_files += 1
        file_rows = 0

        # Ler arquivo conforme seu formato
        try:
            if file_suffix == ".xlsx":
                # XLSX: carregar tudo (geralmente menor volume)
                df = pd.read_excel(file)
                chunks = [df]  # Simular iteração com lista
            else:
                # CSV/TXT: ler em chunks para economizar memória
                chunks = pd.read_csv(
                    file, 
                    sep=";", 
                    chunksize=100_000, 
                    encoding="latin1"
                )
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file.name}: {e}")
            continue

        # Processar cada chunk
        for chunk in chunks:
            chunk = normalize_columns(chunk)

            if "DESCRICAO" not in chunk.columns:
                logger.warning(f"Coluna DESCRICAO não encontrada em {file.name}")
                continue

            # Filtrar apenas despesas
            chunk_filtered = chunk[chunk["DESCRICAO"].apply(is_despesa)].copy()

            if chunk_filtered.empty:
                continue

            # Tratar colunas numéricas se existirem
            if 'VL_SALDO_FINAL' in chunk_filtered.columns:
                chunk_filtered['VL_SALDO_FINAL'] = _clean_numeric(chunk_filtered['VL_SALDO_FINAL'])
                n_invalid = chunk_filtered['VL_SALDO_FINAL'].isna().sum()
                if n_invalid:
                    logger.info(f"  {n_invalid:,} valores inválidos em VL_SALDO_FINAL em {file.name}")

            if 'VL_SALDO_INICIAL' in chunk_filtered.columns:
                chunk_filtered['VL_SALDO_INICIAL'] = _clean_numeric(chunk_filtered['VL_SALDO_INICIAL'])

            # Criar coluna padrão `ValorDespesas` para facilitar as etapas seguintes
            if 'ValorDespesas' not in chunk_filtered.columns:
                if 'VL_SALDO_FINAL' in chunk_filtered.columns:
                    chunk_filtered['ValorDespesas'] = chunk_filtered['VL_SALDO_FINAL']
                else:
                    # criar coluna nula caso não exista
                    chunk_filtered['ValorDespesas'] = pd.NA

            # Salvar chunk processado (usar ponto-e-vírgula e quoting para evitar quebra de colunas)
            import csv as _csv
            chunk_filtered.to_csv(
                OUTPUT_FILE,
                mode="a",
                index=False,
                header=not OUTPUT_FILE.exists(),
                sep=';',
                quoting=_csv.QUOTE_MINIMAL,
                quotechar='"',
                encoding='utf-8'
            )

            rows_written = len(chunk_filtered)
            file_rows += rows_written
            total_rows += rows_written

        if file_rows > 0:
            logger.info(f"  ✓ {file_rows:,} registros salvos de {file.name}")
        else:
            logger.warning(f"  ⚠ Nenhum registro de despesa encontrado em {file.name}")

    logger.info(f"Processamento finalizado: {total_rows:,} registros de {total_files} arquivo(s)")
