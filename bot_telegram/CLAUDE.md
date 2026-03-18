# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot + AI agent system for e-commerce business intelligence. It enables free-form data queries and automated daily reports via Telegram, using Claude API for SQL generation and data narrative.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Required `.env` variables:
- `TELEGRAM` — Telegram bot token
- `POSTGRES_URL` — Supabase PostgreSQL connection string
- `ANTHROPIC_API_KEY` — Claude API key
- `CHAT_ID` — Auto-populated on first bot interaction

## Running

**Bot interativo (polling):**
```bash
python agente.py
```

**Relatório standalone (sem bot — para cron):**
```bash
python agente.py --relatorio
```

**Agendamento via cron:**
```bash
0 8 * * * cd /path/to/project && .venv/bin/python agente.py --relatorio >> /tmp/agente.log 2>&1
```

## Architecture

```
PostgreSQL (Supabase)
  └── Gold data marts (3 tables)
        │
        ▼
db.py — SQLAlchemy connection + execute_query(sql) — SELECT/WITH only
        │
        ▼
agente.py — arquivo único (IA + bot Telegram)
  ├── chat()              → Claude tool use → SQL dinâmico → resposta
  ├── gerar_relatorio()   → 4 queries fixas → Claude → relatório .md
  ├── enviar_telegram()   → HTTP POST direto à API Telegram (sem bot)
  ├── handlers /start, /relatorio, texto livre
  └── __main__: bot polling (padrão) ou --relatorio (cron)
```

### Key design decisions

- Arquivo único de execução: `python agente.py` sobe o bot; `python agente.py --relatorio` gera e envia relatório (para cron)
- `db.py` valida que apenas `SELECT`/`WITH` são executados (sem mutações)
- Claude usa tool use com limite de 10 iterações por pergunta
- Primeira interação auto-registra `CHAT_ID` no `.env`, habilitando o modo standalone

## Data Layer

Three Gold data marts in PostgreSQL (documented in `.llm/database.md`):

| Table | Purpose |
|---|---|
| `public_gold_sales.vendas_temporais` | Sales metrics by temporal dimension |
| `public_gold_cs.clientes_segmentacao` | Customer segmentation (VIP/TOP_TIER/REGULAR) |
| `public_gold_pricing.precos_competitividade` | Competitive pricing analysis |

The full schema, column definitions, business rules, and example queries are in `.llm/database.md`. The PRD with system prompts and full technical spec is in `.llm/prd.md`.

## Tech Stack

- Python 3.10+
- `anthropic` — Claude API with tool use
- `sqlalchemy` + `psycopg2-binary` — PostgreSQL
- `pandas` + `tabulate` — data formatting
- `python-telegram-bot` v20+ (async)
- `python-dotenv`
