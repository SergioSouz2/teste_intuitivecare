# import_operadoras.py
from pathlib import Path
import csv
import logging
from utils import sanitize_value, is_valid_cnpj, safe_int

logger = logging.getLogger(__name__)

def import_operadoras(conn, data_dir):
    csv_path = Path(data_dir) / "operadoras_ativas.csv"
    if not csv_path.exists():
        logger.warning(f"Arquivo não encontrado: {csv_path}")
        return

    cur = conn.cursor()
    inserted = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                registro_operadora = safe_int(row.get("REGISTRO_OPERADORA"))
                cnpj = sanitize_value(row.get("CNPJ"), 14)
                razao_social = sanitize_value(row.get("Razao_Social"), 255)
                nome_fantasia = sanitize_value(row.get("Nome_Fantasia"), 255)
                modalidade = sanitize_value(row.get("Modalidade"), 100)
                logradouro = sanitize_value(row.get("Logradouro"), 255)
                numero = sanitize_value(row.get("Numero"), 20)
                complemento = sanitize_value(row.get("Complemento"), 100)
                bairro = sanitize_value(row.get("Bairro"), 100)
                cidade = sanitize_value(row.get("Cidade"), 100)
                uf = sanitize_value(row.get("UF"), 20)
                cep = sanitize_value(row.get("CEP"), 8)
                ddd = sanitize_value(row.get("DDD"), 3)
                telefone = sanitize_value(row.get("Telefone"), 20)
                fax = sanitize_value(row.get("Fax"), 20)
                email = sanitize_value(row.get("Endereco_eletronico"), 255)
                representante = sanitize_value(row.get("Representante"), 255)
                cargo_representante = sanitize_value(row.get("Cargo_Representante"), 100)
                regiao = safe_int(row.get("Regiao_de_Comercializacao"))
                data_registro = row.get("Data_Registro_ANS") or None

                if not registro_operadora or not cnpj or not is_valid_cnpj(cnpj) or not razao_social:
                    logger.warning(f"Operadora inválida: {row}")
                    continue

                cur.execute(
                    """
                    INSERT INTO operadoras(
                        registro_operadora, cnpj, razao_social,
                        nome_fantasia, modalidade, logradouro,
                        numero, complemento, bairro, cidade, uf,
                        cep, ddd, telefone, fax, endereco_eletronico,
                        representante, cargo_representante, regiao_de_comercializacao,
                        data_registro_ans
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (registro_operadora) DO NOTHING
                    """,
                    (
                        registro_operadora, cnpj, razao_social, nome_fantasia,
                        modalidade, logradouro, numero, complemento, bairro, cidade, uf,
                        cep, ddd, telefone, fax, email, representante,
                        cargo_representante, regiao, data_registro
                    )
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Erro ao processar linha {row}: {e}")
                conn.rollback()
                continue

    conn.commit()
    cur.close()
    logger.info(f"Operadoras inseridas: {inserted}")
