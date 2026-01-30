import pandas as pd
import zipfile
import json
from pathlib import Path
from scripts.config import logger, PROCESSED_DIR

INPUT = PROCESSED_DIR / "despesas_normalizadas.csv"
OUTPUT = PROCESSED_DIR / "consolidado_despesas.csv"
ZIP = PROCESSED_DIR / "consolidado_despesas.zip"
AUDIT = PROCESSED_DIR / "auditoria.json"


def consolidate():
    logger.info("Consolidação iniciada")

    audit_log = {}

    # 1. Ler arquivo processado
    try:
        df = pd.read_csv(INPUT, sep=';', encoding='utf-8', on_bad_lines='warn')
        audit_log["total_linhas_lidas"] = len(df)
        logger.info(f"Arquivo lido: {len(df):,} registros")
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {INPUT}")
        raise

    # 2. Converter DATA para datetime
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    linhas_data_invalida = df["DATA"].isnull().sum()
    audit_log["linhas_data_invalida"] = int(linhas_data_invalida)
    logger.info(f"Datas inválidas descartadas: {linhas_data_invalida:,}")

    df = df.dropna(subset=["DATA"])

    # 3. Converter valores monetários
    df["VL_SALDO_FINAL"] = (
        df["VL_SALDO_FINAL"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # 4. Extrair Ano e Trimestre
    df["Ano"] = df["DATA"].dt.year
    df["Trimestre"] = df["DATA"].dt.quarter

    # 5. Remover valores zerados ou negativos
    linhas_valor_zero_negativo = len(df[df["VL_SALDO_FINAL"] <= 0])
    audit_log["linhas_valor_zero_negativo"] = int(linhas_valor_zero_negativo)
    logger.info(f"Valores ≤ 0 descartados: {linhas_valor_zero_negativo:,}")

    df = df[df["VL_SALDO_FINAL"] > 0]

    # 6. Consolidação
    logger.info("Agrupando dados...")
    final = (
        df.groupby(["REG_ANS", "DESCRICAO", "Ano", "Trimestre"], as_index=False)
        .agg({"VL_SALDO_FINAL": "sum"})
    )

    # 7. Renomear e ordenar colunas (conforme enunciado)
    final = final.rename(columns={
        "REG_ANS": "CNPJ",
        "DESCRICAO": "RazaoSocial",
        "VL_SALDO_FINAL": "ValorDespesas"
    })

    final = final[["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"]]
    final = final.sort_values(["Ano", "Trimestre", "CNPJ"])

    # 8. Estatísticas finais
    audit_log["linhas_consolidadas"] = len(final)
    audit_log["cnpjs_unicos"] = int(df["REG_ANS"].nunique())
    audit_log["trimestres_processados"] = int(final["Trimestre"].nunique())
    audit_log["anos_processados"] = int(final["Ano"].nunique())
    audit_log["valor_total"] = float(final["ValorDespesas"].sum())
    audit_log["valor_medio"] = float(final["ValorDespesas"].mean())

    logger.info(f"CNPJs únicos: {audit_log['cnpjs_unicos']:,}")
    logger.info(f"Linhas consolidadas: {audit_log['linhas_consolidadas']:,}")
    logger.info(f"Valor total: R$ {audit_log['valor_total']:,.2f}")

    # 9. Salvar CSV consolidado
    final.to_csv(OUTPUT, index=False)
    logger.info(f"✓ CSV salvo em: {OUTPUT}")

    # 10. Criar ZIP
    try:
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(OUTPUT, OUTPUT.name)
        audit_log["zip_criado"] = True
        logger.info(f"✓ ZIP criado: {ZIP}")
    except Exception as e:
        audit_log["zip_criado"] = False
        logger.warning(f"Erro ao criar ZIP: {e}")

    # 11. Salvar auditoria
    with open(AUDIT, "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Auditoria salva em: {AUDIT}")
    logger.info("Consolidação concluída com sucesso")
