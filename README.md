# IntuitiveCare - Teste de Integração com API Pública da ANS

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

**Pipeline Automatizado de Extração, Transformação e Análise de Dados da ANS**

</div>

---

Projeto que automatiza extração, transformação e análise de dados de saúde suplementar.

---

## Requisitos

- **Python:** 3.8+
- **Sistema:** Linux/Mac/Windows
- **Espaço:** 500 MB mínimo
- **Internet:** Para acesso à API da ANS

---

## Ambiente

### 1. Entrar no diretório

```bash
cd teste_intuitivecare
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar arquivo .env

```bash
echo "BASE_URL=https://dadosabertos.ans.gov.br/FTP/PDA/" > .env
echo "LOG_LEVEL=INFO" >> .env
```

### 5. Validar instalação

```bash
python -c "import pandas, requests, bs4; print('✓ OK')"
```

---

## Git

### Branches Utilizadas

```
main ← etapa_3 ← etapa_2 ← etapa_1
```

**Estratégia:** Uma branch por etapa. Cada etapa é desenvolvida isoladamente e depois mergeada em main.

```bash
# Etapa 1
git checkout -b etapa_1
git add scripts/etapa1/
git commit -m "[feat] Etapa 1: Download, processamento e consolidação"
git checkout main
git merge --no-ff etapa_1

# Etapa 2
git checkout -b etapa_2
git add scripts/etapa2/
git commit -m "[feat] Etapa 2: Enriquecimento, validação e agregação"
git checkout main
git merge --no-ff etapa_2

# Etapa 3
git checkout -b etapa_3
git add scripts/etapa3/
git commit -m "[feat] Etapa 3: Banco de dados e análise"
git checkout main
git merge --no-ff etapa_3
```

**Convenção de commits:** `[tipo] Descrição`

- `[feat]`: Nova funcionalidade
- `[fix]`: Correção
- `[docs]`: Documentação

---

## Docker

### Como Usar

```bash
# Iniciar (a partir da raiz do projeto)
docker-compose up -d

# Verificar status
docker-compose ps

# Conectar ao banco
docker exec -it teste_intuitivecare_db psql -U postgres -d teste_intuitivecare

# Executar script SQL
docker exec teste_intuitivecare_db psql -U postgres -d teste_intuitivecare \
  -f scripts/etapa3/ddl/create_tables.sql

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down

# Parar e remover volumes (limpa dados)
docker-compose down -v
```

### Estrutura

- **docker-compose.yml (raiz)**: Orquestra 2 serviços (postgres + python) em rede compartilhada
- **Dockerfile**: Imagem Python 3.11 com PostgreSQL client
- **init.sql**: Executa DDL na criação do container

**Por que Docker?** Mesmo ambiente para todo mundo. Sem "funciona na minha máquina".

## Estrutura de Dados

```
scripts/
├── config.py                  # Configuração centralizada
├── etapa1/
│   ├── main.py               # Orquestração
│   ├── extract/download.py   # Baixa arquivos
│   ├── transform/processing.py # Normaliza dados
│   ├── consolidate/consolidation.py # Consolida
│   └── analysis/resumo_processado.py # Relatório
├── etapa2/
│   ├── main.py               # Orquestração
│   ├── download.py           # Baixa operadoras
│   ├── enrich.py             # Faz JOIN
│   ├── validate.py           # Valida CNPJ
│   └── aggregate.py          # Calcula estatísticas
├── etapa3/
│   ├── main.py                 # Orquestração da etapa 3
│   ├── ddl/
│   │    └── create_tables.sql  # Criação de tabelas normalizadas com UUID
│   ├── import_csv/
│   │    ├── import_consolidadas.py  # Importação consolidado_despesas.csv
│   │    ├── import_agregadas.py     # Importação despesas_agregadas.csv
│   │    └── import_operadoras.py    # Importação CSV operadoras
│   ├── analysis/
│   │    ├── query1_crescimento.py
│   │    ├── query2_distribuicao_uf.py
│   │    └── query3_acima_media.py
│   └── utils.py               # Funções utilitárias (ex: tratamento de valores nulos, logging)
└── utils/
|   └── date_utils.py         # Utilitários de data
|
data/
├── raw/                       # ZIPs baixados
├── extracted/                 # Arquivos extraídos
└── processed/                 # CSVs finais
    ├── consolidado_despesas.csv         # Etapa 1
    ├── consolidado_enriquecido.csv      # Etapa 2
    ├── consolidado_validado.csv         # Etapa 2
    ├── despesas_agregadas.csv           # Etapa 2
    └── auditoria.json                   # Relatório

logs/
└── app.log                    # Log de execução
```

---

## Etapa 1: Download, Processamento e Consolidação

### 1.1 Baixar os Arquivos

A primeira etapa acessa a **API Pública da ANS** e faz o download dos arquivos de demonstrações contábeis:

```bash
PYTHONPATH=. python scripts/etapa1/main.py
```

**O que acontece:**

- Descobre dinamicamente a URL da API via HTML parsing
- Localiza os últimos 3 trimestres (1T, 2T, 3T)
- Faz download dos arquivos ZIP com streaming (8KB chunks)
- Extrai arquivos (CSV, TXT, XLSX)

**Justificativas Técnicas:**

**1. Descoberta Dinâmica:** A API não expõe endpoint estruturado, então usamos HTML parsing com BeautifulSoup4

- Reduz manutenção: se estrutura da API mudar, função se adapta automaticamente
- Escalável: encontra qualquer trimestre disponível, não hardcoded

**2. Streaming de Download (8KB chunks):**

- Economia de RAM: não carrega arquivo inteiro na memória
- Resumível: se conexão cair, pode retomar do ponto
- Suporta arquivos grandes: sem limite de tamanho
- Alternativa (full buffer): consumiria 200MB+ de memória

**3. Processamento de 3 trimestres:**

- Dados relevantes: últimos 3 trimestres cobrem análise recente
- Histórico: permite análise de tendências trimestral
- Processar todos: demoraria horas, não agregaria valor

**Arquivos criados em `data/raw/` e `data/extracted/`**

### 1.2 Processar

Após o download, os dados são normalizados e limpos:

- **Normalização de colunas:** Padroniza nomes (remove espaços, acentos, caracteres especiais)
- **Conversão de números:** Converte formato brasileiro (1.234,56) para padrão internacional
- **Filtragem de despesas:** Mantém apenas registros com tipo de despesa válida
- **Processamento em chunks:** Lê 100k linhas por vez (eficiência de memória)

**Justificativas Técnicas:**

**1. Normalização de Colunas:**

- Consistência: diferentes CSVs podem ter nomes diferentes para mesma informação
- Processamento downstream: código espera nomes padronizados
- Rastreabilidade: auditoria de quais colunas vieram de onde

**2. Conversão de Números (1.234,56 → 1234.56):**

- Compatibilidade: pandas trabalha com formato inglês
- Cálculos precisos: evita arredondamentos
- Comparações: números em formato padrão comparáveis

**3. Filtragem de Despesas:**

- Reduz ruído: remove linhas que não são despesas (headers duplicados, linhas em branco)
- Foco: apenas dados relevantes para análise
- Performance: menos dados = processamento mais rápido

**4. Processamento em Chunks (100k linhas):**

- Escalável: arquivos de 1GB processados sem crashar
- RAM limitada: mantém ~50MB na memória por vez
- Resiliente: se falhar no meio, sabe onde retomar
- Alternativa (carregar tudo): CSV de 500MB + processamento = Out of Memory

**Por que Chunks?**

Imagine um arquivo CSV com **500 linhas** de despesas:

```
// Approach 1: Carregar Tudo (pd.read_csv)
1. Lê arquivo inteiro → memória
   [linha 1, linha 2, ... linha 500]
2. Processa tudo de uma vez
3. Salva resultado

Problema: Se arquivo tem 10GB → precisa 10GB de RAM
          Se tem apenas 4GB RAM → CRASH
```

```
// Approach 2: Chunks (pd.read_csv(chunksize=100000))
1. Lê 100k linhas → memória
2. Processa essas 100k
3. Salva essas 100k
4. Descarta da memória
5. Lê próximas 100k
6. Repete até fim

Vantagem: RAM máximo ~50MB em uso
          Arquivo de 10GB processado com 4GB de RAM
```

### 1.3 Consolidação

**Por que CNPJ e Razão Social NÃO estão na consolidação?**

A **consolidação focou em dados de despesas puras** pelos seguintes motivos:

1. **Separação de Responsabilidades:** Dados financeiros consolidados em uma etapa, enriquecimento em outra
2. **Deduplicação:** Na consolidação, múltiplas despesas do mesmo CNPJ são agregadas (SUM)
3. **Eficiência:** CNPJ e Razão Social vêm de outra fonte (cadastro de operadoras)
4. **Auditoria:** Mantém separado o que vem da API vs. o que vem do cadastro

**Justificativas Detalhadas:**

**1. Consolidação SEM Dados da Operadora (primeiro):**

```
Trimestres [1T, 2T, 3T] → Mesma Operadora (nº registro)
      ↓
Agrupa por número de registro
      ↓
SUM(despesas) por tipo
      ↓
consolidado_despesas.csv (5-10 MB)
```

**Por que?**

- Simplicidade: foca em fazer UMA coisa bem (consolidação de despesas)
- Reutilização: dados consolidados usáveis mesmo sem enriquecimento
- Rastreabilidade: sabe exatamente qual dado vem de qual API
- Flexibilidade: podem usar cadastro de operadora diferente depois

**2. Enriquecimento depois (LEFT JOIN):**

```
consolidado_despesas.csv
           +
operadoras_ativas.csv (cadastro)
           ↓
LEFT JOIN em número de registro
           ↓
consolidado_enriquecido.csv (com CNPJ + Razão Social)
```

**Por que LEFT JOIN?**

- ✅ Preservação: mantém TODAS as despesas, mesmo se operadora não for encontrada
- ✅ Auditoria: você vê quais operadoras estão faltando no cadastro
- ✅ Completo: resultado tem todas as colunas de ambas as fontes
- ❌ INNER JOIN: perderia dados de operadoras inativas

**3. Dados Redundantes vs. Integrados:**

- Problema: Consolidar com CNPJ direto = dados redundantes (mesmo CNPJ repetido N vezes)
- Solução: Consolidar apenas despesas, depois enriquecer com left join único

**Exemplo:**

```
// Consolidado SEM operadora (despesas agregadas):
nº_registro | trimestre | total_despesas | registros_agregados
123456      | 2025      | 150000         | 5
123456      | 2024      | 120000         | 4

// Depois enriquece com operadora (UMA VEZ):
nº_registro | cnpj              | razao_social | trimestre | total_despesas
123456      | 12.345.678/0001-90| Operadora XY | 2025      | 150000
123456      | 12.345.678/0001-90| Operadora XY | 2024      | 120000
```

**Saída:** `data/processed/consolidado_despesas.csv`

---

## Etapa 2: Enriquecimento, Validação e Agregação

### 2.1 Enriquecimento

A consolidação anterior possui apenas dados financeiros. Agora enriquecemos com informações da operadora:

```bash
PYTHONPATH=. python scripts/etapa2/main.py
```

**O que acontece:**

1. **Lê cadastro de operadoras:** `operadoras_ativas.csv` (baixado da API)
2. **LEFT JOIN com consolidado_despesas.csv:**
   - Campo comum: `número de registro` (da operadora)
   - Resultado: Mantém todas as despesas, adiciona CNPJ e Razão Social
3. **Remove duplicatas:** Se uma operadora tem múltiplos registros, mantém o primeiro
4. **Saída:** `consolidado_enriquecido.csv` (completo com todos os dados)

**Justificativas Técnicas:**

**1. Dados da Operadora em Fonte Separada:**

- Autoridade: CNPJ vem do cadastro oficial da ANS (fonte única de verdade)
- Histórico: consolidação pode agrupar dados, operadora tem 1 registro por operadora
- Manutenção: se mudar dados da operadora, não precisa reprocessar tudo

**2. LEFT JOIN (não INNER JOIN):**

```
consolidado_despesas.csv (100 registros)
        +
operadoras_ativas.csv (95 operadoras)
        ↓
LEFT JOIN
        ↓
Resultado: 100 registros (todos mantidos)
  - 95 com CNPJ encontrado
  - 5 com NaN (operadora inativa ou não encontrada)
```

**Por que LEFT?**

- Rastreabilidade: vê quais despesas não têm operadora correspondente
- Análise: pode investigar por que 5 registros não foram encontrados
- Auditoria: dados não são silenciosamente descartados
- INNER JOIN: perderia 5 registros, não saberia que existem

**3. Remove Duplicatas (drop_duplicates):**

```
Antes:
nº_reg | cnpj | nome
123    | XX   | Operadora A
123    | XX   | Operadora A  ← duplicada

Depois (keep='first'):
nº_reg | cnpj | nome
123    | XX   | Operadora A
```

**Por que?**

- Dados limpos: 1 registro por operadora
- Performance: evita agregações duplicadas depois
- Significado: keep='first' usa registro mais confiável (primeiro na fonte)

**Saída Intermediária:** `consolidado_enriquecido.csv` (agora com CNPJ e Razão Social)

### 2.2 Validação

Com dados enriquecidos, valida a integridade:

**Validações Realizadas:**

1. **CNPJ:** Verifica dígitos verificadores (mod 11)
2. **Formato:** CNPJ válido deve ter 14 dígitos
3. **Valores:** Campos numéricos positivos ou zero
4. **Datas:** Dentro do intervalo esperado
5. **Nulos:** Identifica campos críticos vazios

**Marcação de Inválidos:**

- Registros que falham em qualquer validação são marcados como `"INVÁLIDO"` para facilitar a auditoria. Isso inclui: valores negativos, valores nulos (NULL) ou zero em campos numéricos críticos.
- Permite auditoria: você vê exatamente qual registro é questionável

**Por que não rejeitar?** → Facilita análise de qualidade dos dados e conformidade

**Justificativas Técnicas:**

**1. Validação de CNPJ (algoritmo mod 11):**

```
CNPJ: 12.345.678/0001-90
       ├─ Dígito 1 (mod 11)
       └─ Dígito 2 (mod 11)

Se um dígito não corresponde → CNPJ inválido
```

**Por que mod 11?**

- Padrão oficial: CNPJs brasileiros usam este algoritmo
- Detecta erros: captura 99% dos erros de digitação
- Validação prévia: antes de enviar para API de validação

**2. Validação de Formato (14 dígitos):**

- Estrutura: CNPJ sempre tem 14 dígitos, sem exceção
- Rápido: check de 1 linha (não faz cálculo)
- Rastreabilidade: CNPJs malformados são marcados diferente de CNPJs inválidos

**3. Marcação como "INVÁLIDO" (vs. Rejeitar):**

```
// Opção 1: REJEITAR (INNER filter)
Dados originais: 1000 registros
Válidos: 950 registros
Rejeitados: 50 (perdidos forever)
Problema: Não sabe por que foram rejeitados

// Opção 2: MARCAR (current)
Dados: 1000 registros
status_validacao: 950 "VÁLIDO", 50 "INVÁLIDO"
Vantagem: Todos mantidos, pode analisa depois
```

**Por que Marcar?**

- Conformidade: dados financeiros DEVEM ser auditáveis
- Análise: sabe quantos/quais registros falharam
- Decisão: negócio decide se usa dados "inválidos" ou não
- Rastreamento: facilita investigação de problemas

**4. Validação Independente para Cada Critério:**

```
CNPJ válido? → coluna "validacao_cnpj"
Valores positivos? → coluna "validacao_valores"
Datas corretas? → coluna "validacao_datas"

Status final: "VÁLIDO" só se TUDO passar
```

**Saída:** `consolidado_validado.csv` (com status de validação)

### 2.3 Agregação com Múltiplas Estratégias

A agregação gera estatísticas usando diferentes estratégias:

**Por CNPJ (agregação simples):**

```
CNPJ | Razão Social | Total Despesas | Média | Desvio Padrão | Registros
```

**Estratégias de Cálculo:**

1. **SUM:** Total de despesas por CNPJ
2. **MEAN:** Média de despesas (para comparação de tendências)
3. **STD:** Desvio padrão (mede variabilidade entre registros)
4. **COUNT:** Quantos registros foram agregados

**Filtragem:**

- Remove registros marcados como `"INVÁLIDO"` antes dos cálculos
- Garante que apenas dados validados entram nas estatísticas

**Ordenação:**

- Ordena por total descending (maiores despesas primeiro)

**Justificativas Técnicas:**

**1. Agregação por CNPJ (não por registro individual):**

```
Dados enriquecidos (consolidado_enriquecido.csv):
CNPJ | Trimestre | Despesa | Categoria
XX01 | 1T2025    | 100k    | Pessoal
XX01 | 1T2025    | 50k     | Custeio
XX01 | 2T2025    | 120k    | Pessoal

Agregado (despesas_agregadas.csv):
CNPJ | Total | Média | STD | Registros
XX01 | 270k  | 90k   | 30k | 3
```

**Por que agregado?**

- Síntese: reduz 1000 registros para 100 operadoras
- Análise: facilita comparação entre operadoras
- Performance: agregado cabe em memória, é 10x menor
- Significado: mostra "tamanho" real de cada operadora

**2. Múltiplas Métricas (SUM + MEAN + STD):**

```
// SUM: Total absoluto
Total = 270k
→ Quanto essa operadora gastou em 3 trimestres

// MEAN: Média por trimestre
Média = 90k
→ Gasto médio trimestral (para comparar padrão)

// STD: Desvio padrão
STD = 30k
→ Variabilidade (se STD alto = despesas inconsistentes)
→ Se STD baixo = despesas estáveis
```

**Por que múltiplas?**

- Contexto: SUM sozinho não diz se despesa é consistente ou flutuante
- Análise: STD alto = pode indicar sazonalidade ou irregularidade
- Comparação: pode comparar operadoras por estabilidade (STD) ou volume (SUM)

**3. Filtragem de "INVÁLIDO" Antes da Agregação:**

```
Entrada (consolidado_validado.csv):
100 registros (95 VÁLIDO, 5 INVÁLIDO)
       ↓
Filtra: remove 5 INVÁLIDO
       ↓
Saída (despesas_agregadas.csv):
95 registros agregados por CNPJ
```

**Por que filtrar?**

- Pureza: estatísticas baseadas apenas em dados confiáveis
- Significado: totais e médias não infladas por dados ruins
- Auditoria: você sabe que agregado foi calculado apenas com "VÁLIDO"

**4. Ordenação Descending (maiores primeiro):**

```
CNPJ | Total
XX01 | 500k   ← Topo (maior gasto)
XX02 | 300k
XX03 | 100k
XX04 | 50k    ← Final (menor gasto)
```

**Por que descending?**

- Priorização: operadoras maiores aparecem primeiro
- Análise: focas nos "grandes players" que movem mais dinheiro
- Padrão: relatórios financeiros geralmente mostram maiores primeiro

**Saída Final:** `despesas_agregadas.csv`

---

## Troubleshooting

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError` | Use `PYTHONPATH=. python ...` |
| `Connection refused` | Verifique internet e `.env` |
| `Permission denied` | `chmod +x scripts/etapa1/main.py` |
| `MemoryError` | Feche outros programas |

---

## Etapa 3: Banco de Dados e Análise

### 3.1 Estrutura das Tabelas

#### Diagrama Lógico

```
+-----------------+        +-----------------------+        +----------------------+
|   operadoras    | 1     N|  despesas_consolidadas|        |  despesas_agregadas  |
|-----------------|--------|----------------------|        |--------------------|
| id (UUID, PK)   |<------>| operadora_id (FK)    |        | id (UUID, PK)       |
| cnpj            |        | ano                  |        | operadora_id (FK)   |
| razao_social    |        | trimestre            |        | uf                  |
| nome_fantasia   |        | valor_despesas       |        | total_despesas      |
| ...             |        |                      |        | media_despesas      |
| data_registro   |        |                      |        | desvio_padrao       |
+-----------------+        +----------------------+        +--------------------+
```

---

### 3.2 Trade-offs Técnicos

#### Normalização vs Desnormalização

**Decisão: Normalização (Opção B)**

Optou-se por uma abordagem normalizada, separando dados cadastrais das operadoras e dados financeiros, visando:

- Reduzir redundância: a operadora X não se repete em centenas de linhas
- Facilitar atualizações cadastrais independentemente de dados financeiros
- Melhorar integridade referencial com chaves estrangeiras
- Volume de dados financeiros cresce mais rapidamente que dados cadastrais
- Análises exigem agregações temporais que beneficiam da estrutura normalizada

A performance analítica não é impactada negativamente com índices apropriados.

---

#### Tipos de Dados - Valores Monetários

**Decisão: NUMERIC(20,2)**

Foi utilizado NUMERIC(20,2) para garantir precisão decimal em cálculos financeiros, evitando erros de arredondamento comuns em tipos FLOAT.

| Opção | Vantagem | Desvantagem | Razão da rejeição |
|-------|----------|------------|-------------------|
| NUMERIC(20,2) | ✅ Precisão exata | Mais lento | **ESCOLHIDO** |
| FLOAT | Rápido | Impreciso em centavos | Inaceitável em contexto financeiro |
| INTEGER (centavos) | Rápido e exato | Reduz legibilidade | Aumenta complexidade de queries |

Aplicado em: `valor_despesas`, `total_despesas`, `media_despesas`, `desvio_padrao`

---

#### Tipos de Dados - Datas

**Decisão: DATE**

O tipo DATE foi utilizado para campos de data por representar corretamente o domínio do dado, permitir validações nativas e facilitar operações temporais.

| Tipo | Uso | Razão |
|------|-----|-------|
| **DATE** | `data_registro_ans` | ✅ Correto - só data importa |
| VARCHAR | Evitar | Ambiguidades (DD/MM vs MM/DD) |
| TIMESTAMP | Futuro | Complexidade desnecessária agora |

---

### 3.3 Estrutura das Tabelas

#### Tabela operadoras

```sql
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
```

---

#### Tabela despesas_consolidadas

```sql
CREATE TABLE despesas_consolidadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operadora_id UUID REFERENCES operadoras(id),  
    registro_ans INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    valor_despesas NUMERIC(20,2) NOT NULL
);
```

---

#### Tabela despesas_agregadas

```sql
CREATE TABLE despesas_agregadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operadora_id UUID REFERENCES operadoras(id),
    razao_social VARCHAR(255),
    uf VARCHAR(20),
    total_despesas NUMERIC(20,2),
    media_despesas NUMERIC(20,2),
    desvio_padrao NUMERIC(20,2)
);
```

---

#### Tabelas Pendentes (Quarentena)

```sql
CREATE TABLE despesas_consolidadas_pendentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registro_ans INTEGER,
    ano INTEGER,
    trimestre INTEGER,
    valor_despesas NUMERIC(20,2)
);

CREATE TABLE despesas_agregadas_pendentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    razao_social VARCHAR(255),
    uf VARCHAR(20),
    total_despesas NUMERIC(20,2),
    media_despesas NUMERIC(20,2),
    desvio_padrao NUMERIC(20,2)
);
```

Dados problemáticos (NULL obrigatório, formato inválido, etc.) ficam nestas tabelas para análise e correção manual.

---

### 3.4 Índices e Performance

```sql
CREATE INDEX idx_operadoras_cnpj ON operadoras(cnpj);
CREATE INDEX idx_operadoras_uf ON operadoras(uf);
CREATE INDEX idx_operadoras_registro ON operadoras(registro_operadora);

CREATE INDEX idx_despesas_operadora ON despesas_consolidadas(operadora_id);
CREATE INDEX idx_despesas_ano_trimestre ON despesas_consolidadas(ano, trimestre);

CREATE INDEX idx_agregadas_operadora ON despesas_agregadas(operadora_id);
CREATE INDEX idx_agregadas_uf ON despesas_agregadas(uf);
```

**Lógica dos índices:**

- CNPJ, registro_operadora: campos de busca frequente
- UF: filtros regionais aparecem muito nas análises
- `operadora_id`: chave estrangeira usada em JOINs
- `ano, trimestre`: filtros temporais combinados aparecem juntos

---

### 3.5 Tratamento de Inconsistências

Durante a importação dos CSVs, foram encontrados alguns problemas comuns:

| Problema | Tratamento | Por quê |
|----------|-----------|--------|
| NULL em CNPJ ou razão social | Rejeitar para tabela `_pendentes` | Dados obrigatórios incompletos não devem estar na produção |
| Texto em campo numérico | Tentar conversão; se falhar, rejeitar | Identifica erro na fonte |
| Datas em formato DD/MM/YYYY | Converter para ISO 8601 (YYYY-MM-DD) | Evita ambiguidade com MM/DD/YYYY |
| Espaços em branco extras | TRIM | Dados "sujos" do CSV |
| CNPJ com caracteres especiais | Remover e validar 14 dígitos | CNPJ deve ser apenas número |

**Fluxo:**

1. Dados entram em tabela temporária (sem constraints)
2. Validações limpam e convertem os dados
3. Dados válidos vão para tabelas principais
4. Dados inválidos ficam em `_pendentes` para análise manual

---

### 3.6 Queries Analíticas

#### Query 1: Crescimento de Despesas

**Pergunta:** Quais as 5 operadoras com maior crescimento percentual entre o primeiro e último trimestre?

**Desafio:** Algumas operadoras podem não ter dados em todos os períodos.

**Solução:** Usar INNER JOIN garante que só comparamos operadoras que têm dados nos dois períodos (comparação justa).

```sql
WITH primeiro_trimestre AS (
    SELECT operadora_id, valor_despesas
    FROM despesas_consolidadas
    WHERE (ano, trimestre) = (
        SELECT ano, trimestre 
        FROM despesas_consolidadas 
        ORDER BY ano, trimestre 
        LIMIT 1
    )
),
ultimo_trimestre AS (
    SELECT operadora_id, valor_despesas
    FROM despesas_consolidadas
    WHERE (ano, trimestre) = (
        SELECT ano, trimestre 
        FROM despesas_consolidadas 
        ORDER BY ano DESC, trimestre DESC 
        LIMIT 1
    )
)
SELECT 
    o.razao_social,
    pt.valor_despesas AS despesas_inicio,
    ut.valor_despesas AS despesas_fim,
    ROUND(((ut.valor_despesas - pt.valor_despesas) / pt.valor_despesas * 100), 2) AS crescimento_pct
FROM primeiro_trimestre pt
INNER JOIN ultimo_trimestre ut ON pt.operadora_id = ut.operadora_id
JOIN operadoras o ON pt.operadora_id = o.id
ORDER BY crescimento_pct DESC
LIMIT 5;
```

---

#### Query 2: Distribuição por Estado

**Pergunta:** Qual a distribuição de despesas por UF? Quais os 5 estados com maiores despesas totais?

**Detalhe adicional:** Calcular também a média de despesas por operadora em cada UF.

```sql
SELECT 
    o.uf,
    COUNT(DISTINCT o.id) AS total_operadoras,
    ROUND(SUM(dc.valor_despesas), 2) AS total_despesas_uf,
    ROUND(AVG(dc.valor_despesas), 2) AS media_trimestral,
    ROUND(
        (SELECT AVG(soma_operadora)
         FROM (
            SELECT SUM(dc2.valor_despesas) AS soma_operadora
            FROM despesas_consolidadas dc2
            WHERE dc2.operadora_id IN (
                SELECT id FROM operadoras WHERE uf = o.uf
            )
            GROUP BY dc2.operadora_id
         ) sub
        ), 2
    ) AS media_por_operadora
FROM despesas_consolidadas dc
JOIN operadoras o ON dc.operadora_id = o.id
GROUP BY o.uf
ORDER BY total_despesas_uf DESC
LIMIT 5;
```

**Por que subquery para média por operadora?**
Se fizéssemos `AVG(AVG(...))`, as contas ficariam erradas porque operadoras com mais trimestres pesariam mais na média final. A subquery calcula corretamente: soma por operadora, depois faz média dessas somas.

---

#### Query 3: Operadoras Acima da Média

**Pergunta:** Quantas operadoras tiveram despesas acima da média geral em pelo menos 2 dos 3 trimestres?

```sql
WITH media_geral AS (
    SELECT AVG(valor_despesas) AS media FROM despesas_consolidadas
)
SELECT 
    o.razao_social,
    o.uf,
    COUNT(*) AS trimestres_total,
    COUNT(CASE WHEN dc.valor_despesas > mg.media THEN 1 END) AS acima_media,
    ROUND(AVG(dc.valor_despesas), 2) AS media_operadora
FROM despesas_consolidadas dc
JOIN operadoras o ON dc.operadora_id = o.id
CROSS JOIN media_geral mg
GROUP BY o.id, o.razao_social, o.uf
HAVING COUNT(CASE WHEN dc.valor_despesas > mg.media THEN 1 END) >= 2
ORDER BY acima_media DESC;
```

**Por que CROSS JOIN?** Precisa trazer a média geral para cada linha.

**Por que CASE WHEN dentro de COUNT?** Para contar apenas os trimestres acima da média, não todos.

---

# Etapa 4: API e Interface Web

## 4.1 Visão Geral

Esta etapa expõe os dados processados e consolidados através de uma API RESTful em FastAPI e permite interação via interface web em Vue.js.

### Objetivos

- Permitir consulta de operadoras e histórico de despesas.

- Disponibilizar estatísticas agregadas.

- Criar uma interface amigável para exploração dos dados.

## 4.2 Backend (API)

### 4.2.1 Estrutura de Pastas

```
backend/
├── app/
│   ├── main.py           # Inicializa FastAPI e inclui rotas
│   ├── database.py       # Configuração do SQLAlchemy / conexão com PostgreSQL
│   ├── models/           # Models SQLAlchemy
│   │   ├── operadora.py
│   │   └── despesa.py
│   ├── routes/           # Rotas da API
│   │   └── operadoras.py
│   ├── schemas/          # Pydantic schemas para validação/resposta
│   │   ├── operadora.py
│   │   └── despesa.py
│   └── utils.py          # Funções utilitárias (ex: normalização de CNPJ)
├── requirements.txt
└── .env
```

### 4.2.2 Rotas da API

| Método | Rota | Descrição | Query Params |
|--------|------|-----------|--------------|
| GET | `/api/operadoras` | Lista operadoras com paginação | `page=1`, `limit=10`, `uf=SP` (opcional) |
| GET | `/api/operadoras/{cnpj}` | Detalhes de uma operadora | - |
| GET | `/api/operadoras/{cnpj}/despesas` | Histórico de despesas | - |
| GET | `/api/estatisticas` | Estatísticas gerais (total, média, top 5) | - |
| GET | `/api/estatisticas/uf` | Distribuição por UF | - |
| GET | `/api/estatisticas/crescimento` | Operadoras com maior crescimento | - |


### 4.2.3 Exemplos de Uso (cURL)

- Listar operadoras (paginação)

```
curl -X GET "http://127.0.0.1:8000/api/operadoras?page=1&limit=10" -H "accept: application/json"
````

- Detalhes de uma operadora pelo CNPJ

```
curl -X GET "http://127.0.0.1:8000/api/operadoras/22027346000116" -H "accept: application/json"
```

- Despesas de uma operadora

```
curl -X GET "http://127.0.0.1:8000/api/estatisticas" -H "accept: application/json"
```

- Estatísticas agregadas

```
curl -X GET "http://127.0.0.1:8000/api/operadoras/22027346000116/despesas" -H "accept: application/json"
```

### 4.2.4 Decisões Técnicas do Backend

-Framework: FastAPI

    - ✅ Suporte a async, documentação automática (/docs), validação automática com     Pydantic.

    - Justificativa: alto desempenho e facilidade de manutenção.

- Paginação: Offset-based

    - Simples de implementar e suficiente para volumes médios.

    - Cursor-based/Keyset seriam opcionais se o volume crescer para milhões de registros.

- Cache de Estatísticas: Resultado armazenado por X minutos

    - Evita cálculos repetidos para grandes volumes.

    - Mantém consistência razoável com atualização periódica.

- Estrutura de Resposta: Pydantic schemas garantindo:
```
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "operadoras": [ ... ]
}
```




## 4.3 Como Executar o Backend

### 4.3.1 Instalação e Setup

```bash
# 1. Entrar no diretório backend
cd backend

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/teste_intuitivecare
LOG_LEVEL=INFO
CACHE_TTL=300
EOF

# 5. Rodar servidor
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Servidor estará disponível em:** `http://localhost:8000`

**Documentação interativa:** `http://localhost:8000/docs` (Swagger)

### 4.3.2 Fluxo de Execução

1. **FastAPI inicia** em `app/main.py`
2. **Conecta ao PostgreSQL** via SQLAlchemy (database.py)
3. **Carrega models** (operadora.py, despesa.py)
4. **Registra rotas** (operadoras.py, estatisticas.py)
5. **Inicia servidor** na porta 8000

### 4.3.3 Validação da API

```bash
# Verificar se está rodando
curl http://localhost:8000/docs

# Teste simples
curl http://localhost:8000/api/operadoras?page=1&limit=5
```

---

## 4.4 Frontend (Vue.js)

### 4.4.1 Estrutura de Componentes

```
src/
├── App.vue                    # Componente raiz
├── main.js                    # Entry point
├── router/
│   └── index.js              # Vue Router (navegação entre páginas)
├── store/
│   ├── index.js              # Pinia store setup
│   └── operadoras.js         # State management de operadoras
├── views/
│   ├── Operadoras.vue        # Lista paginada de operadoras
│   ├── DetalhesOperadora.vue # Detalhes + histórico de despesas
│   └── Estatisticas.vue      # Gráficos e estatísticas
├── components/
│   └── Navbar.vue            # Barra de navegação
└── assets/
    └── styles.css            # Estilos globais
```

### 4.4.2 Componentes e Suas Funções

#### `App.vue` (Raiz)

- Renderiza o Navbar e router-view
- Setup inicial de tema/configurações globais

#### `Navbar.vue` (Navegação)

- Links para as 3 pages: Operadoras, Detalhes, Estatísticas
- Estilo consistente em todas as páginas

#### `Operadoras.vue` (Lista Paginada)

**Funcionalidades:**
- Tabela com paginação (offset-based)
- Busca por CNPJ ou Razão Social
- Filtro por UF
- Clique na linha → vai para DetalhesOperadora

**Estratégia de Busca:** Híbrida
- Busca básica no cliente (CNPJ/Razão Social)
- Filtro por UF no servidor (reduz dados transferidos)

**Gerenciamento de Estado:** Pinia
- Store `operadoras.js` centraliza estado
- Dados carregados uma vez, reutilizados

```javascript
// store/operadoras.js (pseudo-código)
export const useOperadorasStore = defineStore('operadoras', () => {
  const operadoras = ref([]);
  const currentPage = ref(1);
  const limit = ref(10);
  const total = ref(0);
  
  const fetchOperadoras = async (page, limit, uf = null) => {
    const response = await fetch(
      `/api/operadoras?page=${page}&limit=${limit}&uf=${uf}`
    );
    const data = await response.json();
    operadoras.value = data.operadoras;
    total.value = data.total;
  };
  
  return { operadoras, currentPage, limit, total, fetchOperadoras };
});
```

#### `DetalhesOperadora.vue` (Página Detalhes)

**Funcionalidades:**
- Exibe informações da operadora (CNPJ, Razão Social, UF, Modalidade)
- Tabela com histórico de despesas por trimestre
- Botão "Voltar" para Operadoras

**Fluxo:**
1. Recebe CNPJ via URL (router.params.cnpj)
2. Fetch `/api/operadoras/{cnpj}` → detalhes
3. Fetch `/api/operadoras/{cnpj}/despesas` → histórico

#### `Estatisticas.vue` (Dashboard)

**Funcionalidades:**
- **Cards de Resumo:** Total de despesas, número de operadoras, média por operadora
- **Gráfico de Distribuição:** Pizza/Barras com despesas por UF (top 10)
- **Tabela de Top 5:** Top 5 operadoras por despesa

**Biblioteca de Gráfico:** Chart.js ou Vue-Chartjs

```javascript
// Exemplo de gráfico de pizza (UF distribution)
<script setup>
import { Pie } from 'vue-chartjs';

const chartData = {
  labels: ['SP', 'RJ', 'MG', 'BA', 'RS'],
  datasets: [{
    data: [500000, 300000, 250000, 200000, 150000],
    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
  }]
};
</script>
```

### 4.4.3 Como Executar o Frontend

```bash
# 1. Entrar no diretório frontend
cd frontend

# 2. Instalar dependências
npm install

# 3. Rodar servidor de desenvolvimento
npm run dev
```

**Servidor estará disponível em:** `http://localhost:5173` (Vite default)

### 4.4.4 Build para Produção

```bash
npm run build
```

Gera pasta `dist/` com arquivos otimizados.

### 4.4.5 Decisões Técnicas do Frontend

**Gerenciamento de Estado: Pinia**
- ✅ Simples, moderno, compatível com Vue 3
- Alternativas consideradas:
  - Props/Events: muito verboso para 3 páginas
  - Vuex: overkill, mais complexo

**Busca/Filtro: Híbrido**
- Cliente: busca por CNPJ (instant feedback)
- Servidor: filtro por UF (reduz dados)
- Justificativa: melhor UX sem sobrecarregar servidor

**Performance da Tabela: Paginação (offset-based)**
- ✅ Simples, rápida para <100k registros
- Cursor-based se crescer para milhões

**Tratamento de Erros:**
```javascript
// Exemplo em Operadoras.vue
const fetchOperadoras = async () => {
  try {
    const response = await fetch(`/api/operadoras?page=${page}`);
    if (!response.ok) {
      showError('Erro ao carregar operadoras');
      return;
    }
    const data = await response.json();
    operadoras.value = data.operadoras;
  } catch (error) {
    showError(`Erro de rede: ${error.message}`);
  }
};
```

---

## 4.5 Integração Frontend + Backend

### 4.5.1 Fluxo de Dados

```
Vue.js (Frontend)
   ↓ HTTP Request (JSON)
FastAPI (Backend)
   ↓ SQLAlchemy Query
PostgreSQL (Database)
   ↓ JSON Response
Vue.js (Renderiza)
```

### 4.5.2 Exemplo: Buscar Operadoras

**Frontend (Operadoras.vue):**
```javascript
const fetchOperadoras = async (page = 1) => {
  const response = await fetch(
    `http://localhost:8000/api/operadoras?page=${page}&limit=10`
  );
  const data = await response.json();
  operadorasStore.setOperadoras(data.operadoras);
};
```

**Backend (app/routes/operadoras.py):**
```python
@router.get("/operadoras")
async def list_operadoras(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    operadoras = db.query(Operadora).skip(skip).limit(limit).all()
    total = db.query(Operadora).count()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "operadoras": operadoras
    }
```

### 4.5.3 Pré-requisitos para Integração

1. **Backend rodando:** `http://localhost:8000`
2. **Frontend rodando:** `http://localhost:5173`
3. **CORS habilitado** no FastAPI:

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---


### 4.6.3 Como Usar no Postman

1. Importe a coleção
2. Verifique que o backend está rodando (`http://localhost:8000`)
3. Click em cada requisição e click em **Send**
4. Veja respostas esperadas

---

## 5. Executar Projeto Completo

### 5.1 Order Correta de Execução

```bash
# 1. Terminal 1 - Banco de dados (Docker)
cd teste_intuitivecare
docker-compose up -d

# 2. Terminal 2 - Backend (Flask/FastAPI)
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# 3. Terminal 3 - Frontend (Vue.js)
cd frontend
npm run dev

# 4. Abrir browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

### 5.2 Fluxo de Testes

1. **Abra** `http://localhost:5173` no navegador
2. **Clique** em "Operadoras" → vê lista paginada
3. **Busque** por CNPJ ou UF
4. **Clique** em uma operadora → vê detalhes e despesas
5. **Vá para** "Estatísticas" → vê gráficos e top 5

---

## 6. Trade-offs Técnicos Documentados

| Aspecto | Opção Escolhida | Alternativas | Justificativa |
|---------|-----------------|--------------|---------------|
| **Framework Backend** | FastAPI | Flask, Django | Async nativo, documentação automática, validação automática |
| **Paginação** | Offset-based | Cursor-based, Keyset | Simples e suficiente para <100k registros |
| **Cache Estatísticas** | Redis 5min | Sempre calcular, Pré-calcular BD | Balanço entre frescura e performance |
| **Estado Frontend** | Pinia | Props/Events, Vuex | Moderno, simples para 3 pages |
| **Busca/Filtro** | Híbrido | Servidor, Cliente | Melhor UX sem sobrecarregar servidor |
| **Tipo de Dado ($$)** | NUMERIC(20,2) | FLOAT, INTEGER | Precisão exata essencial para valores financeiros |
| **Normalização DB** | Normalizada | Desnormalizada | Reduz redundância, facilita manutenção |

---

---

## Troubleshooting

| Erro | Solução |
|------|---------|
| `Port 8000 already in use` | `lsof -i :8000` para matar processo, ou mude porta |
| `CORS error` | Verifique `allow_origins` no FastAPI |
| `TypeError: Cannot read property 'operadoras'` | Aguarde resposta da API antes de renderizar |
| `Database connection refused` | Verifique Docker está rodando: `docker-compose ps` |
| `Module not found (Pinia, Chart.js)` | Rode `npm install` no frontend |

---

## Conclusão

Projeto completo de **extração, transformação, análise e visualização de dados de saúde suplementar**, cobrindo:


