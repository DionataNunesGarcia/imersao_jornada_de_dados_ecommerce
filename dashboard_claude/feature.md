# Feature Plan: E-commerce Analytics Dashboard

Dashboard Streamlit com 3 páginas para diretores de um e-commerce, consumindo os data marts Gold do Supabase.

---

## Arquivos a criar

```
case-01-dashboard/
├── app.py           # App completo (única entrada)
├── requirements.txt # Dependências Python
└── .env.example     # Template de variáveis de ambiente
```

---

## Passo a passo

### 1. `requirements.txt`

Criar o arquivo de dependências:

```
streamlit
psycopg2-binary
pandas
plotly
python-dotenv
```

---

### 2. `.env.example`

Template de variáveis de ambiente:

```
SUPABASE_HOST=seu-host.supabase.co
SUPABASE_PORT=5432
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=sua-senha
```

---

### 3. `app.py` — Estrutura base

- `st.set_page_config(layout="wide", page_title="E-commerce Analytics")`
- Função `get_connection()` — lê `.env` via `python-dotenv`, retorna conexão psycopg2. Exibe `st.error()` amigável se falhar
- Função `run_query(sql)` — executa query e retorna `pd.DataFrame`. Fecha conexão após uso
- Função `fmt_brl(valor)` — formata número no padrão brasileiro (`R$ 1.234,56`)
- Sidebar com título "E-commerce Analytics" e `st.sidebar.radio` com as 3 páginas
- Router: chama função da página selecionada

---

### 4. Página: Vendas

**Fonte:** `public_gold_sales.vendas_temporais`

**Filtro:**
- `st.selectbox` de mês (`mes_venda`) no topo — opção "Todos" inclusa
- Filtragem aplicada no DataFrame antes dos cálculos

**KPIs** (`st.columns(4)`):

| Métrica | Cálculo |
|---|---|
| Receita Total | `SUM(receita_total)` → `fmt_brl` |
| Total de Vendas | `SUM(total_vendas)` → inteiro com ponto de milhar |
| Ticket Médio | Receita Total / Total de Vendas → `fmt_brl` |
| Clientes Únicos | `MAX(total_clientes_unicos)` por `data_venda`, depois soma → inteiro |

**Gráfico 1 — Receita Diária** (`px.line`):
- X: `data_venda` | Y: `SUM(receita_total)` agrupado por `data_venda`

**Gráfico 2 — Receita por Dia da Semana** (`px.bar`):
- X: `dia_semana_nome` (ordem: Segunda → Domingo) | Y: `SUM(receita_total)`
- Ordem manual com `pd.Categorical`

**Gráfico 3 — Volume de Vendas por Hora** (`px.bar`):
- X: `hora_venda` (0–23) | Y: `SUM(total_vendas)`

---

### 5. Página: Clientes

**Fonte:** `public_gold_cs.clientes_segmentacao`

**Filtro:**
- `st.selectbox` de segmento (VIP / TOP_TIER / REGULAR / Todos) — afeta apenas a tabela detalhada

**KPIs** (`st.columns(4)`):

| Métrica | Cálculo |
|---|---|
| Total Clientes | `COUNT(*)` |
| Clientes VIP | `COUNT(*) WHERE segmento = 'VIP'` |
| Receita VIP | `SUM(receita_total) WHERE segmento = 'VIP'` → `fmt_brl` |
| Ticket Médio Geral | `AVG(ticket_medio)` → `fmt_brl` |

**Gráfico 1 — Distribuição por Segmento** (`px.pie`):
- Valores: `COUNT(*)` por `segmento_cliente`

**Gráfico 2 — Receita por Segmento** (`px.bar`):
- X: `segmento_cliente` | Y: `SUM(receita_total)`

**Gráfico 3 — Top 10 Clientes** (`px.bar`, horizontal):
- Y: `nome_cliente` (top 10 por `ranking_receita`) | X: `receita_total`
- `orientation='h'`

**Gráfico 4 — Clientes por Estado** (`px.bar`):
- X: `estado` | Y: `COUNT(*)`, ordenado decrescente

**Tabela detalhada:**
- `st.dataframe` com todas as colunas, filtrado pelo selectbox de segmento

---

### 6. Página: Pricing

**Fonte:** `public_gold_pricing.precos_competitividade`

**Filtro:**
- `st.multiselect` de categoria (Eletrônicos, Casa, Moda, Games, Cozinha, Beleza, Acessórios)
- Filtragem aplicada no DataFrame antes dos cálculos

**KPIs** (`st.columns(4)`):

| Métrica | Cálculo |
|---|---|
| Total Produtos Monitorados | `COUNT(*)` |
| Mais Caros que Todos | `COUNT(*) WHERE classificacao = 'MAIS_CARO_QUE_TODOS'` |
| Mais Baratos que Todos | `COUNT(*) WHERE classificacao = 'MAIS_BARATO_QUE_TODOS'` |
| Diferença Média vs Mercado | `AVG(diferenca_percentual_vs_media)` → `+X,X%` |

**Gráfico 1 — Posicionamento vs Concorrência** (`px.pie`):
- Valores: `COUNT(*)` por `classificacao_preco`

**Gráfico 2 — Competitividade por Categoria** (`px.bar`):
- X: `categoria` | Y: `AVG(diferenca_percentual_vs_media)`
- Barras verdes para negativo (mais barato), vermelhas para positivo (mais caro)
- Usar `color_discrete_map` ou `color` condicional

**Gráfico 3 — Competitividade × Volume de Vendas** (`px.scatter`):
- X: `diferenca_percentual_vs_media` | Y: `quantidade_total`
- Cor: `classificacao_preco` | Tamanho: `receita_total`

**Tabela de alertas:**
- `st.dataframe` apenas com `classificacao_preco = 'MAIS_CARO_QUE_TODOS'`
- Colunas: `produto_id`, `nome_produto`, `categoria`, `nosso_preco`, `preco_maximo_concorrentes`, `diferenca_percentual_vs_media`

---

## Ordem de execução

1. `requirements.txt`
2. `.env.example`
3. `app.py` — estrutura base + conexão + helpers
4. `app.py` — Página Vendas
5. `app.py` — Página Clientes
6. `app.py` — Página Pricing
