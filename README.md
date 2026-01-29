# IntuitiveCare - Teste de Download de Demonstrações Contábeis

## Visão Geral

Este projeto automatiza o download de **Demonstrações Contábeis da ANS** (Agência Nacional de Saúde Suplementar) a partir da API REST disponível em `https://dadosabertos.ans.gov.br/FTP/PDA/`.

---

## Status das Etapas

### Etapa 1.1: Download Automatizado de Demonstrações Contábeis - **CONCLUÍDO**

**Objetivo:** Acessar a API REST e baixar os arquivos de demonstrações contábeis dos últimos 3 trimestres disponíveis.

**O que foi implementado:**

 **Acesso à API REST**

- Conecta ao endpoint: `https://dadosabertos.ans.gov.br/FTP/PDA/`
- Localiza automaticamente a pasta `demonstrações_contabeis`
- Navega pela estrutura de anos (2007-2025)

 **Identificação de Trimestres**

- Busca arquivos no padrão: `QT_YYYY.zip` (ex: `1T2025.zip`, `4T2024.zip`)
- Ordena do mais recente para o mais antigo
- Seleciona os 3 últimos trimestres disponíveis

 **Download Resiliente**

- Implementa timeout (30 segundos) para downloads longos
- Trata erros de conexão e I/O
- Stream download para evitar sobrecarga de memória
- Salva arquivos em `data/raw/`

 **Logging Detalhado**

- Registra todas as operações em arquivo (`logs/app.log`) e console
- Fornece feedback em tempo real do progresso
- Diferencia erros, avisos e informações

 **Configuração via Variáveis de Ambiente**

- BASE_URL configurável no arquivo `.env`
- Facilita mudanças de URL sem editar código

---

## Como Executar

### Pré-requisitos

- Python 3.8+
- pip ou pip3
- Acesso à internet (para baixar os arquivos)

### 1. Instalação de Dependências

#### Opção A: Instalação Global (apt)

```bash
sudo apt install python3-requests python3-bs4 python3-dotenv
```

#### Opção B: Usando Virtual Environment (Recomendado)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar o ambiente
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração

Crie um arquivo `.env` na raiz do projeto baseado no modelo abaixo:

```dotenv
BASE_URL=https://dadosabertos.ans.gov.br/FTP/PDA/
```

Se precisar alterar a URL ou usar um servidor diferente, edite o arquivo `.env`.

### 3. Executar o Script

```bash
python3 scripts/download_any.py
```

**Saída esperada:**

```
INFO: ============================================================
INFO: INICIANDO DOWNLOAD DE DEMONSTRAÇÕES CONTÁBEIS
INFO: ============================================================
INFO: Pasta encontrada: https://dadosabertos.ans.gov.br/FTP/PDA/demonstrações_contabeis/
INFO: Buscando trimestres do ano 2025...
INFO:   ✓ 3T2025.zip
INFO:   ✓ 2T2025.zip
INFO:   ✓ 1T2025.zip
INFO: Iniciando download de 3 arquivo(s)
INFO: Baixando: 3T2025.zip
INFO: ✓ Arquivo salvo: data/raw/3T2025.zip
INFO: Baixando: 2T2025.zip
INFO: ✓ Arquivo salvo: data/raw/2T2025.zip
INFO: Baixando: 1T2025.zip
INFO: ✓ Arquivo salvo: data/raw/1T2025.zip
INFO: ✓ Download concluído com sucesso!
```

---

## 📁 Estrutura do Projeto

```
teste_intuitivecare/
├── README.md                  # Este arquivo
├── .env                       # Variáveis de ambiente (BASE_URL)
├── requirements.txt           # Dependências do projeto
├── scripts/
│   └── download_any.py       # Script principal de download
├── data/
│   ├── raw/                  # Arquivos baixados (3 últimos trimestres)
│   └── processed/            # Para processamento futuro
└── logs/
    └── app.log              # Log detalhado de todas as operações
```

---

##  Arquivos Baixados

Os arquivos são salvos em `data/raw/` com os nomes:

- `1T2025.zip` - 1º Trimestre de 2025
- `2T2025.zip` - 2º Trimestre de 2025
- `3T2025.zip` - 3º Trimestre de 2025

Cada arquivo contém as demonstrações contábeis das operadoras de saúde suplementar.

---

## 🔍 Validação da Etapa 1.1

### Checklist de Requisitos

| Requisito | Status | Detalhes |
|-----------|--------|----------|
| Acessar API REST |  | Conecta via `requests` com timeout |
| Localizar demonstrações_contabeis |  | Busca automática por "demonstra" no HTML |
| Identificar últimos 3 trimestres |  | Ordena por ano/trimestre em reverso |
| Download dos arquivos |  | Stream download com erro handling |
| Estrutura YYYY/QT/ |  | Navega por anos e identifica trimestres |
| Resiliência a variações |  | Try-except em cada etapa, logs de avisos |
| Arquivo de log |  | `logs/app.log` com timestamp e nível |



## Detalhes Técnicos

### Fluxo de Execução

```
main()
├─ find_demonstracoes_contabeis_url()
│  └─ GET https://dadosabertos.ans.gov.br/FTP/PDA/
│     └─ Parse HTML e busca por "demonstra"
│
├─ get_last_trimesters()
│  ├─ GET https://...demonstrações_contabeis/
│  ├─ Parse anos (2007-2025)
│  ├─ Para cada ano:
│  │  └─ GET https://...ano/
│  │     └─ Parse arquivos .zip
│  └─ Ordena e retorna top 3
│
└─ download_files()
   ├─ Para cada arquivo:
   │  ├─ GET arquivo.zip (stream)
   │  └─ Salva em data/raw/
   └─ Log de sucesso/erro
```

### Tratamento de Erros

| Erro | Ação |
|------|------|
| Folder not found | RuntimeError com log de erro |
| Connection timeout | Warning e skip para próximo item |
| Invalid zip name | Skip silencioso (tratado) |
| Disk write error | Error log e skip |

### Logging

- **Arquivo:** `logs/app.log`
- **Formato:** `timestamp | LEVEL | message`
- **Níveis:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Saída:** Simultânea em arquivo e console

---

## Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| requests | >=2.25.0 | HTTP requests |
| beautifulsoup4 | >=4.9.0 | HTML parsing |
| python-dotenv | >=0.19.0 | Carregar .env |

---



