from pathlib import Path
import re
import pandas as pd
from typing import Tuple, Optional

def extract_year_quarter(file: Path, df: Optional[pd.DataFrame] = None) -> Tuple[Optional[int], Optional[int]]:
    """
    Prioridade:
    1️⃣ Nome do arquivo (ex: 1T2025.csv)
    2️⃣ Coluna DATA
    """

    # 1️⃣ Nome do arquivo → 1T2025.csv
    name = file.name.upper()
    m = re.search(r"([1-4])T(20\d{2})", name)
    if m:
        trimestre = int(m.group(1))
        ano = int(m.group(2))
        return ano, trimestre

    # 2️⃣ Coluna DATA (fallback)
    if df is not None and "DATA" in df.columns:
        if not df["DATA"].isna().all():
            data_col = df["DATA"].dropna()
            ano = data_col.dt.year.iloc[0]
            trimestre = data_col.dt.quarter.iloc[0]
            return ano, trimestre

    return None, None
