import pandas as pd
import zipfile
import json
from scripts.config import logger, PROCESSED_DIR

INPUT = PROCESSED_DIR / "despesas_normalizadas.csv"
OUTPUT = PROCESSED_DIR / "consolidado_despesas.csv"
ZIP_FILE = PROCESSED_DIR / "consolidado_despesas.zip"
AUDIT = PROCESSED_DIR / "auditoria.json"


def consolidate():
    logger.info("Consolidação iniciada")

    df = pd.read_csv(INPUT, sep=";", low_memory=False)

    # Garantir tipo numérico
    df["ValorDespesas"] = pd.to_numeric(
        df["ValorDespesas"],
        errors="coerce"
    )

    linhas_antes = len(df)

    # Manter apenas valores válidos
    df = df[df["ValorDespesas"] > 0]

  


    # Consolidação
    final = (
        df.groupby(
            ["RegistroANS", "Ano", "Trimestre"],
            as_index=False
        )
        .agg({
            "ValorDespesas": "sum"
        })
    )

    final.to_csv(
        OUTPUT,
        index=False,
        sep=";",
        encoding="utf-8"
    )

    # Compactação
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(OUTPUT, OUTPUT.name)

    # Auditoria
    audit = {
        "linhas_lidas": int(linhas_antes),
        "linhas_validas": int(len(df)),
        "linhas_consolidadas": int(len(final)),
        "operadoras_unicas": int(final["RegistroANS"].nunique()),
        "anos_processados": sorted(final["Ano"].dropna().unique().tolist()),
        "trimestres_processados": sorted(final["Trimestre"].dropna().unique().tolist()),
        "valor_total": float(final["ValorDespesas"].sum()),
        "valor_medio": float(final["ValorDespesas"].mean())
    }

    with open(AUDIT, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    logger.info(" Consolidação concluída com sucesso")
