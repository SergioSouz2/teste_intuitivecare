from pathlib import Path
import pandas as pd

P = Path("data/processed/despesas_normalizadas.csv")


def main(path: Path = P, top_n: int = 10):
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}")

    df = pd.read_csv(path)

    total_rows = len(df)
    unique_cnpjs = df['REG_ANS'].nunique() if 'REG_ANS' in df.columns else df.get('CNPJ', pd.Series()).nunique()

    # Valor total (tenta colunas possíveis)
    if 'ValorDespesas' in df.columns:
        total_value = df['ValorDespesas'].sum()
    elif 'VL_SALDO_FINAL' in df.columns:
        # tenta converter
        total_value = pd.to_numeric(df['VL_SALDO_FINAL'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').sum()
    else:
        total_value = None

    print(f"Total de registros: {total_rows:,}")
    print(f"CNPJs únicos: {unique_cnpjs:,}")
    if total_value is not None:
        print(f"Valor total (soma): R$ {total_value:,.2f}")
    else:
        print("Valor total: coluna não encontrada")

    print("\nTop N CNPJs por soma de valores:")
    if 'ValorDespesas' in df.columns:
        grp = df.groupby('CNPJ')['ValorDespesas'].sum().sort_values(ascending=False).head(top_n)
        print(grp.to_string())
    elif 'REG_ANS' in df.columns and 'VL_SALDO_FINAL' in df.columns:
        vals = pd.to_numeric(df['VL_SALDO_FINAL'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
        grp = df.assign(_val=vals).groupby('REG_ANS')['_val'].sum().sort_values(ascending=False).head(top_n)
        print(grp.to_string())
    else:
        print("Impossível calcular top CNPJs: colunas esperadas não encontradas.")


if __name__ == '__main__':
    main()