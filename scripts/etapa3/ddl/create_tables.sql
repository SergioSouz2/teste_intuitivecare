
-- Operadoras
-- Ativa extensão para gerar UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";;


-- Tabela Operadoras (nomes exatamente iguais ao CSV)
CREATE TABLE IF NOT EXISTS operadoras (
    "ID" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "REGISTRO_OPERADORA" INTEGER UNIQUE NOT NULL,
    "CNPJ" VARCHAR(14) NOT NULL,
    "Razao_Social" VARCHAR(255) NOT NULL,
    "Nome_Fantasia" VARCHAR(255),
    "Modalidade" VARCHAR(100),
    "Logradouro" VARCHAR(255),
    "Numero" VARCHAR(20),
    "Complemento" VARCHAR(100),
    "Bairro" VARCHAR(100),
    "Cidade" VARCHAR(100),
    "UF" CHAR(2),
    "CEP" VARCHAR(8),
    "DDD" VARCHAR(3),
    "Telefone" VARCHAR(20),
    "Fax" VARCHAR(20),
    "Endereco_eletronico" VARCHAR(255),
    "Representante" VARCHAR(255),
    "Cargo_Representante" VARCHAR(100),
    "Regiao_de_Comercializacao" INTEGER,
    "Data_Registro_ANS" DATE
);

-- Índices para acelerar consultas
CREATE INDEX IF NOT EXISTS idx_operadoras_cnpj ON operadoras("CNPJ");
CREATE INDEX IF NOT EXISTS idx_operadoras_uf ON operadoras("UF");
CREATE INDEX IF NOT EXISTS idx_operadoras_registro ON operadoras("REGISTRO_OPERADORA");
