"""
Cria os schemas e tabelas gold no Supabase e importa os dados dos CSVs.
Executar uma vez: python3 setup_gold.py
"""
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(_BASE_DIR, ".env"), override=True)

CSVS_DIR = os.path.join(_BASE_DIR, "..", "tabelas gold")


def get_connection():
    url = os.getenv("POSTGRES_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        port=os.getenv("SUPABASE_PORT", 5432),
        dbname=os.getenv("SUPABASE_DB", "postgres"),
        user=os.getenv("SUPABASE_USER"),
        password=os.getenv("SUPABASE_PASSWORD"),
    )


DDL = """
-- Schemas
CREATE SCHEMA IF NOT EXISTS public_gold_sales;
CREATE SCHEMA IF NOT EXISTS public_gold_cs;
CREATE SCHEMA IF NOT EXISTS public_gold_pricing;

-- vendas_temporais
CREATE TABLE IF NOT EXISTS public_gold_sales.vendas_temporais (
    data_venda               DATE        NOT NULL,
    ano_venda                INTEGER     NOT NULL,
    mes_venda                INTEGER     NOT NULL,
    dia_venda                INTEGER     NOT NULL,
    dia_semana_nome          VARCHAR     NOT NULL,
    hora_venda               INTEGER     NOT NULL,
    receita_total            NUMERIC     NOT NULL,
    quantidade_total         INTEGER     NOT NULL,
    total_vendas             INTEGER     NOT NULL,
    total_clientes_unicos    INTEGER     NOT NULL,
    ticket_medio             NUMERIC     NOT NULL
);

-- clientes_segmentacao
CREATE TABLE IF NOT EXISTS public_gold_cs.clientes_segmentacao (
    cliente_id          VARCHAR     NOT NULL,
    nome_cliente        VARCHAR,
    estado              VARCHAR(2),
    receita_total       NUMERIC     NOT NULL,
    total_compras       INTEGER     NOT NULL,
    ticket_medio        NUMERIC     NOT NULL,
    primeira_compra     DATE        NOT NULL,
    ultima_compra       DATE        NOT NULL,
    segmento_cliente    VARCHAR     NOT NULL,
    ranking_receita     INTEGER     NOT NULL
);

-- precos_competitividade
CREATE TABLE IF NOT EXISTS public_gold_pricing.precos_competitividade (
    produto_id                      VARCHAR     NOT NULL,
    nome_produto                    VARCHAR     NOT NULL,
    categoria                       VARCHAR     NOT NULL,
    marca                           VARCHAR     NOT NULL,
    nosso_preco                     NUMERIC     NOT NULL,
    preco_medio_concorrentes        NUMERIC,
    preco_minimo_concorrentes       NUMERIC,
    preco_maximo_concorrentes       NUMERIC,
    total_concorrentes              INTEGER     NOT NULL,
    diferenca_percentual_vs_media   NUMERIC,
    diferenca_percentual_vs_minimo  NUMERIC,
    classificacao_preco             VARCHAR     NOT NULL,
    receita_total                   NUMERIC     NOT NULL,
    quantidade_total                INTEGER     NOT NULL
);
"""


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()
    print("Schemas e tabelas criados.")


def load_csv(conn, csv_path, schema, table):
    df = pd.read_csv(csv_path)
    print(f"  Carregando {len(df)} linhas em {schema}.{table}...")

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {schema}.{table}")
        cols = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f"INSERT INTO {schema}.{table} ({cols}) VALUES ({placeholders})"
        rows = [tuple(None if pd.isna(v) else v for v in row) for row in df.itertuples(index=False)]
        cur.executemany(insert_sql, rows)

    conn.commit()
    print(f"  OK — {schema}.{table}")


def main():
    print("Conectando ao banco...")
    conn = get_connection()
    print("Conexão OK.\n")

    print("Criando tabelas...")
    create_tables(conn)

    print("\nImportando CSVs...")
    load_csv(conn, os.path.join(CSVS_DIR, "vendas_temporais_rows.csv"),
             "public_gold_sales", "vendas_temporais")
    load_csv(conn, os.path.join(CSVS_DIR, "clientes_segmentacao_rows.csv"),
             "public_gold_cs", "clientes_segmentacao")
    load_csv(conn, os.path.join(CSVS_DIR, "precos_competitividade_rows.csv"),
             "public_gold_pricing", "precos_competitividade")

    conn.close()
    print("\nSetup concluído! Execute: streamlit run app.py")


if __name__ == "__main__":
    main()
