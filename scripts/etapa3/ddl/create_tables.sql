-- ---------------------------
-- EXTENSÕES
-- ---------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------
-- DROP TABLES EXISTENTES
-- ---------------------------
DROP TABLE IF EXISTS despesas_agregadas;
DROP TABLE IF EXISTS despesas_agregadas_pendentes;

DROP TABLE IF EXISTS despesas_consolidadas;
DROP TABLE IF EXISTS despesas_consolidadas_pendentes;  
DROP TABLE IF EXISTS operadoras;

-- ---------------------------
-- TABELA OPERADORAS
-- ---------------------------
CREATE TABLE operadoras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registro_operadora INTEGER UNIQUE NOT NULL,
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf VARCHAR(20),
    cep VARCHAR(8),
    ddd VARCHAR(3),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(255),
    representante VARCHAR(255),
    cargo_representante VARCHAR(100),
    regiao_de_comercializacao INTEGER,
    data_registro_ans DATE
);

-- Índices
CREATE INDEX idx_operadoras_cnpj ON operadoras(cnpj);
CREATE INDEX idx_operadoras_uf ON operadoras(uf);
CREATE INDEX idx_operadoras_registro ON operadoras(registro_operadora);

-- ---------------------------
-- TABELA DESPESAS CONSOLIDADAS
-- ---------------------------
CREATE TABLE despesas_consolidadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operadora_id UUID REFERENCES operadoras(id),  
    registro_ans INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    valor_despesas NUMERIC(20,2) NOT NULL
);

CREATE INDEX idx_despesas_operadora ON despesas_consolidadas(operadora_id);
CREATE INDEX idx_despesas_ano_trimestre ON despesas_consolidadas(ano, trimestre);

-- ---------------------------
-- TABELA DESPESAS PENDENTES
-- ---------------------------
CREATE TABLE despesas_consolidadas_pendentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registro_ans INTEGER,
    ano INTEGER,
    trimestre INTEGER,
    valor_despesas NUMERIC(20,2)
);



-- ---------------------------
-- TABELA DESPESAS AGREGADAS
-- ---------------------------
CREATE TABLE despesas_agregadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operadora_id UUID REFERENCES operadoras(id),
    razao_social VARCHAR(255),
    uf VARCHAR(20),
    total_despesas NUMERIC(20,2),
    media_despesas NUMERIC(20,2),
    desvio_padrao NUMERIC(20,2)
);

CREATE INDEX idx_agregadas_operadora ON despesas_agregadas(operadora_id);
CREATE INDEX idx_agregadas_uf ON despesas_agregadas(uf);



CREATE TABLE IF NOT EXISTS despesas_agregadas_pendentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    razao_social VARCHAR(255),
    uf VARCHAR(20),
    total_despesas NUMERIC(20,2),
    media_despesas NUMERIC(20,2),
    desvio_padrao NUMERIC(20,2)
);
