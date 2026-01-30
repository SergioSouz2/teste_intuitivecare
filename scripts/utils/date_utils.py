from pathlib import Path
import re
import pandas as pd
from typing import Tuple, Optional

def extract_year_quarter(file: Path, df: Optional[pd.DataFrame] = None) -> Tuple[Optional[int], Optional[int]]:
    """
    Extrai Ano e Trimestre do arquivo/pasta. Usa coluna DATA se existir, senão
    tenta extrair do caminho ou nome do arquivo.
    """
    if df is not None and "DATA" in df.columns:
        if not df["DATA"].isna().all():
            data_col = df["DATA"].copy()
            # Preenche NaT com forward fill compatível
            data_col = data_col.ffill()
            ano = data_col.dt.year.iloc[0]
            trimestre = data_col.dt.quarter.iloc[0]
            return ano, trimestre

    # Extrair do caminho
    parts = file.parts
    year = None
    quarter = None
    for p in parts:
        y_match = re.match(r"(20\d{2})", p)
        q_match = re.match(r"Q([1-4])", p.upper())
        if y_match:
            year = int(y_match.group(1))
        if q_match:
            quarter = int(q_match.group(1))

    # Extrair do nome do arquivo
    if year is None or quarter is None:
        m = re.search(r"(20\d{2})[^\d]?Q([1-4])", file.name.upper())
        if m:
            year = int(m.group(1))
            quarter = int(m.group(2))

    return year, quarter
