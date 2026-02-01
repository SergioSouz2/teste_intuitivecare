from pathlib import Path
import csv
import logging
from utils import sanitize_value, is_valid_cnpj

logger = logging.getLogger("pipeline")

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
                # Mapear diretamente do CSV
                registro_operadora = row.get("REGISTRO_OPERADORA")
                cnpj = sanitize_value(row.get("CNPJ"), 14)
                razao_social = sanitize_value(row.get("Razao_Social"), 255)
                nome_fantasia = sanitize_value(row.get("Nome_Fantasia"), 255)
                modalidade = sanitize_value(row.get("Modalidade"), 100)
                logradouro = sanitize_value(row.get("Logradouro"), 255)
                numero = sanitize_value(row.get("Numero"), 20)
                complemento = sanitize_value(row.get("Complemento"), 100)
                bairro = sanitize_value(row.get("Bairro"), 100)
                cidade = sanitize_value(row.get("Cidade"), 100)
                uf = sanitize_value(row.get("UF"), 2)
                cep = sanitize_value(row.get("CEP"), 8)
                ddd = sanitize_value(row.get("DDD"), 3)
                telefone = sanitize_value(row.get("Telefone"), 20)
                fax = sanitize_value(row.get("Fax"), 20)
                email = sanitize_value(row.get("Endereco_eletronico"), 255)
                representante = sanitize_value(row.get("Representante"), 255)
                cargo_representante = sanitize_value(row.get("Cargo_Representante"), 100)

                # Campos que podem ser nulos
                regiao = row.get("Regiao_de_Comercializacao")
                regiao = int(regiao) if regiao and regiao.isdigit() else None

                data_registro = row.get("Data_Registro_ANS")
                data_registro = data_registro if data_registro else None

                # Validações
                if not registro_operadora or not registro_operadora.isdigit():
                    logger.warning(f"Registro inválido: {row}")
                    continue
                if not cnpj or not is_valid_cnpj(cnpj) or not razao_social:
                    logger.warning(f"Operadora inválida: {row}")
                    continue

                # Insert isolado
                try:
                    cur.execute(
                        """
                        INSERT INTO operadoras(
                            "REGISTRO_OPERADORA", "CNPJ", "Razao_Social",
                            "Nome_Fantasia", "Modalidade", "Logradouro",
                            "Numero", "Complemento", "Bairro", "Cidade", "UF",
                            "CEP", "DDD", "Telefone", "Fax", "Endereco_eletronico",
                            "Representante", "Cargo_Representante", "Regiao_de_Comercializacao",
                            "Data_Registro_ANS"
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT ("REGISTRO_OPERADORA") DO NOTHING
                        """,
                        (
                            int(registro_operadora), cnpj, razao_social, nome_fantasia,
                            modalidade, logradouro, numero, complemento, bairro, cidade, uf,
                            cep, ddd, telefone, fax, email, representante,
                            cargo_representante, regiao, data_registro
                        )
                    )
                    inserted += 1
                except Exception as e:
                    logger.error(f"Erro ao importar operadora {registro_operadora}: {e}")
                    conn.rollback()
                    continue

            except Exception as e:
                logger.error(f"Erro processando linha: {row} | {e}")
                continue

    conn.commit()
    cur.close()
    logger.info(f"Operadoras inseridas com sucesso: {inserted}")
