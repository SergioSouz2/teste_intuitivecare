from pathlib import Path
import pandas as pd

P = Path("data/processed/despesas_normalizadas.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.width', None)


def main(path: Path = P, n_head: int = 50):
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}")

    print(f"Carregando: {path}")

    # Ler todo o CSV (assumindo que já foi reduzido em processamento incremental)
    df = pd.read_csv(path)

    print("\n=== Primeiras linhas ===\n")
    print(df.head(n_head).to_string())

    print("\n=== Info ===\n")
    print(df.info())

    print("\n=== Estatísticas (numéricas) ===\n")
    with pd.option_context('display.max_rows', 200):
        print(df.select_dtypes(include=['number']).describe().to_string())

    print("\n=== Top 20 Despesas por Valor ===\n")

    # Garantir colunas de Ano/Trimestre: se ausentes, tentar extrair de `DATA`
    if 'Ano' not in df.columns or 'Trimestre' not in df.columns:
        if 'DATA' in df.columns:
            try:
                df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
                df = df.dropna(subset=['DATA'])
                df['Ano'] = df['DATA'].dt.year
                df['Trimestre'] = df['DATA'].dt.quarter
            except Exception:
                # não conseguir extrair, seguir adiante sem Ano/Trimestre
                pass

    # Garantir coluna numérica de valores: ValorDespesas ou VL_SALDO_FINAL (converter se necessário)
    if 'ValorDespesas' in df.columns:
        val_col = 'ValorDespesas'
    elif 'VL_SALDO_FINAL' in df.columns:
        # tentar converter para numérico (tratando milhares e vírgulas)
        try:
            df['VL_SALDO_FINAL_NUM'] = pd.to_numeric(
                df['VL_SALDO_FINAL'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
                errors='coerce'
            )
            val_col = 'VL_SALDO_FINAL_NUM'
        except Exception:
            val_col = 'VL_SALDO_FINAL'
    else:
        val_col = None

    if val_col is None:
        print("Coluna de valores não encontrada.")
        return

    top = df.sort_values(val_col, ascending=False).head(20)

    # Escolher colunas a exibir conforme disponibilidade
    if set(['CNPJ','RazaoSocial','Ano','Trimestre', val_col]).issubset(top.columns):
        print(top[['CNPJ','RazaoSocial','Ano','Trimestre', val_col]].to_string())
    elif set(['REG_ANS','DESCRICAO','Ano','Trimestre', val_col]).issubset(top.columns):
        print(top[['REG_ANS','DESCRICAO','Ano','Trimestre', val_col]].to_string())
    else:
        # Exibir as colunas mais informativas disponíveis
        cols = [c for c in ['REG_ANS','CNPJ','DESCRICAO','RazaoSocial','DATA','Ano','Trimestre', val_col] if c in top.columns]
        print(top[cols].to_string())


if __name__ == '__main__':
    main()