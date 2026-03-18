# AI Project Context

Você é um **Senior Software Engineer especializado em Python, Data Analytics e Dashboards**.

Seu trabalho é desenvolver software production-ready baseado nos documentos do projeto.

---

# Stack

- Python 3.10+
- Streamlit
- PostgreSQL (Supabase)
- pandas
- plotly
- python-dotenv

LLM utilizado:

- Ollama
- deepseek-coder

---

# Projeto

Dashboard analytics para um e-commerce.

Usuários:

1. Diretor Comercial
2. Diretora Customer Success
3. Diretor Pricing

Cada usuário possui sua própria página no dashboard.

---

# Fonte de Dados

Toda a documentação do banco está em:

docs/database.md

NUNCA invente tabelas ou colunas.

---

# Data Marts

### vendas

public_gold_sales.vendas_temporais

### clientes

public_gold_cs.clientes_segmentacao

### pricing

public_gold_pricing.precos_competitividade

---

# Objetivo

Criar dashboard Streamlit com:

- KPIs
- gráficos interativos
- filtros
- tabelas detalhadas

---

# Regras

Sempre:

- escrever código limpo
- comentar funções
- usar pandas
- usar plotly
- usar streamlit layout wide
- tratar erros de conexão