import pandas as pd
from scripts.config import logger


def enriquecer_com_operadoras(
    df_consolidado: pd.DataFrame,
    df_operadoras: pd.DataFrame
) -> pd.DataFrame:

    logger.info("Iniciando enriquecimento com dados das operadoras")

    # ----------------------------
    # 1. Validação de colunas
    # ----------------------------
    if "RegistroANS" not in df_consolidado.columns:
        raise ValueError("Coluna RegistroANS não encontrada no consolidado")

    if "REGISTRO_OPERADORA" not in df_operadoras.columns:
        raise ValueError("Coluna REGISTRO_OPERADORA não encontrada no cadastro ANS")

    # ----------------------------
    # 2. Padronização de tipos
    # ----------------------------
    df_consolidado["RegistroANS"] = (
        df_consolidado["RegistroANS"]
        .astype(str)
        .str.strip()
    )

    df_operadoras["REGISTRO_OPERADORA"] = (
        df_operadoras["REGISTRO_OPERADORA"]
        .astype(str)
        .str.strip()
    )

    # ----------------------------
    # 3. Tratar duplicidades no cadastro
    # Estratégia: manter 1 linha por operadora
    # ----------------------------
    df_operadoras = (
        df_operadoras
        .sort_values("CNPJ")
        .drop_duplicates(
            subset="REGISTRO_OPERADORA",
            keep="first"
        )
    )

    # ----------------------------
    # 4. Enriquecimento (LEFT JOIN)
    # ----------------------------
    df_enriquecido = df_consolidado.merge(
        df_operadoras[
            ["REGISTRO_OPERADORA", "CNPJ", "Razao_Social", "Modalidade", "UF"]
        ],
        how="left",
        left_on="RegistroANS",
        right_on="REGISTRO_OPERADORA"
    )

    # ----------------------------
    # 5. Padronização final de colunas
    # ----------------------------
    df_final = (
        df_enriquecido
        .rename(columns={"Razao_Social": "RAZAO_SOCIAL"})
        .drop(columns=["REGISTRO_OPERADORA"])
    )

    logger.info("Enriquecimento concluído com sucesso")

    return df_final
