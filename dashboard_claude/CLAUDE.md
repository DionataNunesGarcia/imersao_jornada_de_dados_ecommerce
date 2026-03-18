# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Streamlit analytics dashboard for an e-commerce business, serving 3 directors with self-service access to PostgreSQL (Supabase) Gold data marts. The app is defined in `.llm/prd-dashboard.md` and the database schema is documented in `.llm/database.md`.

## Running the App

```bash
cd case-01-dashboard
cp .env.example .env
# Fill in Supabase credentials in .env
pip install -r requirements.txt
streamlit run app.py
```

Dashboard runs at `http://localhost:8501`.

## Environment Variables

The `.env` file (root-level) currently uses `POSTGRES_URL`. The PRD specifies individual vars:

```
SUPABASE_HOST=
SUPABASE_PORT=5432
SUPABASE_DB=postgres
SUPABASE_USER=
SUPABASE_PASSWORD=
```

## Architecture

```
Supabase PostgreSQL (Gold layer)
    ├── public_gold_sales.vendas_temporais        → Página: Vendas
    ├── public_gold_cs.clientes_segmentacao       → Página: Clientes
    └── public_gold_pricing.precos_competitividade → Página: Pricing
                    ↓
        case-01-dashboard/app.py (single-file Streamlit app)
```

Navigation via `st.sidebar` selectbox. All data fetched via psycopg2 → pandas DataFrames. No aggressive caching — data changes after each `dbt run`.

## Key Implementation Rules (from PRD)

- `st.set_page_config(layout="wide")`
- Brazilian number formatting: R$ with `.` as thousands separator and `,` as decimal (e.g. `R$ 1.234,56`)
- Show connection errors gracefully instead of crashing
- Consistent chart colors across pages (use plotly)

## Data Mart Quick Reference

| Data Mart | Schema | Key Columns |
|---|---|---|
| `vendas_temporais` | `public_gold_sales` | `data_venda`, `receita_total`, `total_vendas`, `ticket_medio`, `total_clientes_unicos`, `dia_semana_nome`, `hora_venda`, `mes_venda` |
| `clientes_segmentacao` | `public_gold_cs` | `cliente_id`, `nome_cliente`, `estado`, `receita_total`, `segmento_cliente` (VIP/TOP_TIER/REGULAR), `ranking_receita`, `ticket_medio` |
| `precos_competitividade` | `public_gold_pricing` | `produto_id`, `categoria`, `nosso_preco`, `classificacao_preco`, `diferenca_percentual_vs_media`, `receita_total`, `quantidade_total` |

**Segmentation thresholds:** VIP ≥ R$10.000 | TOP_TIER ≥ R$5.000 | REGULAR < R$5.000

**Price classifications:** `MAIS_CARO_QUE_TODOS`, `ACIMA_DA_MEDIA`, `NA_MEDIA`, `ABAIXO_DA_MEDIA`, `MAIS_BARATO_QUE_TODOS`

**`ticket_medio`** in `vendas_temporais` = `AVG` per individual transaction, not `receita_total / total_vendas`.

## Documentation

- `.llm/prd-dashboard.md` — full product requirements with KPIs, charts, filters, and SQL per page
- `.llm/database.md` — complete schemas, business rules, sample data, and ready-to-use queries for all 3 data marts
