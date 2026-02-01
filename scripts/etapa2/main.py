import pandas as pd

from scripts.config import logger, PROCESSED_DIR
from scripts.etapa2.download import download_operadoras
from scripts.etapa2.enrich import enriquecer_com_operadoras
from scripts.etapa2.validate import validar_dados
from scripts.etapa2.aggregate import agregar_despesas


def main():
    logger.info("PIPELINE ETAPA 2 INICIADO")

    # -------------------------------------------------
    # 1. Download do cadastro de operadoras (ANS)
    # -------------------------------------------------
    operadoras_path = download_operadoras()

    # -------------------------------------------------
    # 2. Leitura do consolidado financeiro (Teste 1.3)
    # -------------------------------------------------
    consolidado_path = PROCESSED_DIR / "consolidado_despesas.csv"

    df_consolidado = pd.read_csv(
        consolidado_path,
        sep=";",
        low_memory=False
    )

    # -------------------------------------------------
    # 3. Leitura do cadastro de operadoras
    # -------------------------------------------------
    df_operadoras = pd.read_csv(
        operadoras_path,
        sep=";",
        low_memory=False
    )

    # -------------------------------------------------
    # 4. Enriquecimento dos dados
    # (aqui completamos RazaoSocial, RegistroANS, UF...)
    # -------------------------------------------------
    df_enriquecido = enriquecer_com_operadoras(
        df_consolidado=df_consolidado,
        df_operadoras=df_operadoras
    )

    enriquecido_path = PROCESSED_DIR / "consolidado_enriquecido.csv"
    df_enriquecido.to_csv(
        enriquecido_path,
        index=False,
        sep=";",
        encoding="utf-8"
    )

    logger.info(f"Arquivo enriquecido salvo em: {enriquecido_path}")

    # -------------------------------------------------
    # 5. Validação dos dados
    # -------------------------------------------------
    df_validado = validar_dados(df_enriquecido)

    validado_path = PROCESSED_DIR / "consolidado_validado.csv"
    df_validado.to_csv(
        validado_path,
        index=False,
        sep=";",
        encoding="utf-8"
    )

    logger.info(f"Arquivo validado salvo em: {validado_path}")

    # -------------------------------------------------
    # 6. Agregação de despesas
    # -------------------------------------------------
    df_agregado = agregar_despesas(df_validado)

    agregado_path = PROCESSED_DIR / "despesas_agregadas.csv"
    df_agregado.to_csv(
        agregado_path,
        index=False,
        sep=";",
        encoding="utf-8"
    )

    logger.info(f"Arquivo agregado salvo em: {agregado_path}")

    logger.info("PIPELINE ETAPA 2 FINALIZADO COM SUCESSO")


if __name__ == "__main__":
    main()
