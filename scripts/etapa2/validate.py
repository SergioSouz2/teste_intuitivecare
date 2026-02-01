import pandas as pd
from scripts.config import logger

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
    if not cnpj or cnpj in ["INVÁLIDO", "0"]:
        return "INVÁLIDO"
    cnpj = "".join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14:
        return "INVÁLIDO"
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ por dígitos verificadores"""
    if not cnpj:
        return False
    cnpj = "".join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6] + pesos_1

    def calc_digito(base, pesos):
        soma = sum(int(base[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    dig1 = calc_digito(cnpj[:12], pesos_1)
    dig2 = calc_digito(cnpj[:12] + dig1, pesos_2)

    return cnpj[-2:] == dig1 + dig2

def validar_dados(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Validação de dados iniciada")

    # CNPJ
    df["CNPJ"] = df["CNPJ"].apply(
        lambda x: formatar_cnpj(x) if validar_cnpj(x) else "INVÁLIDO"
    )

    # RAZAO_SOCIAL
    df["RAZAO_SOCIAL"] = df["RAZAO_SOCIAL"].apply(
        lambda x: x.strip() if isinstance(x, str) and x.strip() != "" else "INVÁLIDO"
    )

    # Modalidade e UF
    df["Modalidade"] = df["Modalidade"].apply(
        lambda x: x if isinstance(x, str) and x.strip() != "" else "INVÁLIDO"
    )
    df["UF"] = df["UF"].apply(
        lambda x: x if isinstance(x, str) and x.strip() != "" else "INVÁLIDO"
    )

    # ValorDespesas
    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    df["ValorDespesas"] = df["ValorDespesas"].apply(
        lambda x: x if x > 0 else "INVÁLIDO"
    )

    logger.info("Validação concluída e arquivo salvo em: consolidado_validado.csv")
    return df
