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
└── utils/
    └── date_utils.py         # Utilitários de data

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


## Troubleshooting

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError` | Use `PYTHONPATH=. python ...` |
| `Connection refused` | Verifique internet e `.env` |
| `Permission denied` | `chmod +x scripts/etapa1/main.py` |
| `MemoryError` | Feche outros programas |

---



