import pandas as pd
import zipfile
import json
from scripts.config import logger, PROCESSED_DIR
from scripts.utils.date_utils import extract_year_quarter
from pathlib import Path

INPUT = PROCESSED_DIR / "despesas_normalizadas.csv"
OUTPUT = PROCESSED_DIR / "consolidado_despesas.csv"
ZIP = PROCESSED_DIR / "consolidado_despesas.zip"
AUDIT = PROCESSED_DIR / "auditoria.json"

def consolidate():
    logger.info("Consolidação iniciada")
    df = pd.read_csv(INPUT, sep=";", low_memory=False)
    # Converter valores
    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"].astype(str).str.replace(".", "").str.replace(",", "."), errors="coerce")
    df = df[df["ValorDespesas"] > 0]
    # Garantir Ano/Trimestre
    anos = []
    trimestres = []
    for idx, row in df.iterrows():
        file_path = Path(row.get("FilePath", ""))
        ano, trimestre = extract_year_quarter(file_path)
        anos.append(ano)
        trimestres.append(trimestre)
    df["Ano"] = df["Ano"].fillna(pd.Series(anos))
    df["Trimestre"] = df["Trimestre"].fillna(pd.Series(trimestres))
    # Agrupamento
    final = df.groupby(["CNPJ", "RazaoSocial", "Ano", "Trimestre"], as_index=False).agg({"ValorDespesas": "sum"})
    final.to_csv(OUTPUT, index=False)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(OUTPUT, OUTPUT.name)
    # Auditoria
    audit = {
        "linhas_lidas": int(len(df)),
        "linhas_consolidadas": int(len(final)),
        "cnpjs_unicos": int(final["CNPJ"].nunique()),
        "anos_processados": int(final["Ano"].nunique()),
        "trimestres_processados": int(final["Trimestre"].nunique()),
        "valor_total": float(final["ValorDespesas"].sum()),
        "valor_medio": float(final["ValorDespesas"].mean())
    }
    with open(AUDIT, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    logger.info("Consolidação concluída")
