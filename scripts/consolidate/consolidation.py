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
    
    if not INPUT.exists():
        logger.warning(f"{INPUT} não encontrado. Consolidação abortada.")
        return

    df = pd.read_csv(INPUT, sep=";", low_memory=False)
    
    if df.empty:
        logger.warning("CSV vazio. Nada a consolidar.")
        return

    # Converter valores
    df["ValorDespesas"] = pd.to_numeric(
        df.get("ValorDespesas", 0).astype(str).str.replace(".", "").str.replace(",", "."),
        errors="coerce"
    )
    
    df = df[df["ValorDespesas"] > 0]
    if df.empty:
        logger.warning("Todos os valores inválidos ou <= 0. Nada a consolidar.")
        return
    
    # Preencher Ano/Trimestre
    anos = []
    trimestres = []
    for idx, row in df.iterrows():
        file_path = Path(row.get("FilePath", "")) if "FilePath" in df.columns else Path("")
        ano, trimestre = extract_year_quarter(file_path)
        anos.append(ano)
        trimestres.append(trimestre)
    df["Ano"] = df["Ano"].fillna(pd.Series(anos))
    df["Trimestre"] = df["Trimestre"].fillna(pd.Series(trimestres))

    # Padronizar RazaoSocial se coluna existir
    if "RazaoSocial" in df.columns and "CNPJ" in df.columns:
        df["RazaoSocial"] = df.groupby("CNPJ")["RazaoSocial"].transform(lambda x: x.ffill().bfill().iloc[0])
    else:
        df["RazaoSocial"] = ""
        if "CNPJ" not in df.columns:
            logger.warning("CNPJ não encontrado. Consolidação pode ficar incompleta.")
            df["CNPJ"] = ""

    # Agrupamento seguro
    final = df.groupby(["CNPJ", "Ano", "Trimestre"], as_index=False).agg({
        "RazaoSocial": "first",
        "ValorDespesas": "sum"
    })
    final = final[["CNPJ", "RazaoSocial", "Ano", "Trimestre", "ValorDespesas"]]
    
    final.to_csv(OUTPUT, index=False, sep=";")
    
    # Compacta
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
