import os
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(_BASE_DIR, ".env"), override=True)

st.set_page_config(layout="wide", page_title="E-commerce Analytics")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def run_query(sql: str) -> pd.DataFrame:
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        st.stop()


def fmt_brl(valor: float) -> str:
    """Formata número no padrão brasileiro: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(valor: float) -> str:
    """Formata inteiro com ponto de milhar: 1.234"""
    return f"{int(valor):,}".replace(",", ".")


def fmt_pct(valor: float) -> str:
    """Formata percentual com sinal: +1,23% ou -1,23%"""
    sinal = "+" if valor >= 0 else ""
    return f"{sinal}{valor:.2f}%".replace(".", ",")


# ---------------------------------------------------------------------------
# Página: Vendas
# ---------------------------------------------------------------------------

def page_vendas():
    st.title("Vendas")

    df = run_query("SELECT * FROM public_gold_sales.vendas_temporais")

    meses = sorted(df["mes_venda"].unique())
    opcoes_mes = ["Todos"] + [str(m) for m in meses]
    sel_mes = st.selectbox("Mês", opcoes_mes)

    if sel_mes != "Todos":
        df = df[df["mes_venda"] == int(sel_mes)]

    receita_total = df["receita_total"].sum()
    total_vendas = df["total_vendas"].sum()
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    clientes_unicos = df.groupby("data_venda")["total_clientes_unicos"].max().sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita Total", fmt_brl(receita_total))
    c2.metric("Total de Vendas", fmt_int(total_vendas))
    c3.metric("Ticket Médio", fmt_brl(ticket_medio))
    c4.metric("Clientes Únicos", fmt_int(clientes_unicos))

    st.divider()

    # Gráfico 1 — Receita Diária
    df_dia = df.groupby("data_venda", as_index=False)["receita_total"].sum()
    fig1 = px.line(df_dia, x="data_venda", y="receita_total", title="Receita Diária",
                   labels={"data_venda": "Data", "receita_total": "Receita (R$)"})
    st.plotly_chart(fig1, use_container_width=True)

    col_a, col_b = st.columns(2)

    # Gráfico 2 — Receita por Dia da Semana
    ordem_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    df_semana = df.groupby("dia_semana_nome", as_index=False)["receita_total"].sum()
    df_semana["dia_semana_nome"] = pd.Categorical(df_semana["dia_semana_nome"],
                                                   categories=ordem_semana, ordered=True)
    df_semana = df_semana.sort_values("dia_semana_nome")
    fig2 = px.bar(df_semana, x="dia_semana_nome", y="receita_total",
                  title="Receita por Dia da Semana",
                  labels={"dia_semana_nome": "Dia", "receita_total": "Receita (R$)"})
    col_a.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3 — Volume de Vendas por Hora
    df_hora = df.groupby("hora_venda", as_index=False)["total_vendas"].sum()
    fig3 = px.bar(df_hora, x="hora_venda", y="total_vendas",
                  title="Volume de Vendas por Hora",
                  labels={"hora_venda": "Hora", "total_vendas": "Vendas"})
    col_b.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Página: Clientes
# ---------------------------------------------------------------------------

def page_clientes():
    st.title("Clientes")

    df = run_query("SELECT * FROM public_gold_cs.clientes_segmentacao")

    total_clientes = len(df)
    clientes_vip = len(df[df["segmento_cliente"] == "VIP"])
    receita_vip = df[df["segmento_cliente"] == "VIP"]["receita_total"].sum()
    ticket_medio = df["ticket_medio"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Clientes", fmt_int(total_clientes))
    c2.metric("Clientes VIP", fmt_int(clientes_vip))
    c3.metric("Receita VIP", fmt_brl(receita_vip))
    c4.metric("Ticket Médio Geral", fmt_brl(ticket_medio))

    st.divider()

    col_a, col_b = st.columns(2)

    # Gráfico 1 — Distribuição por Segmento
    df_seg = df.groupby("segmento_cliente", as_index=False).size().rename(columns={"size": "total"})
    fig1 = px.pie(df_seg, names="segmento_cliente", values="total",
                  title="Distribuição de Clientes por Segmento", hole=0.3)
    col_a.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2 — Receita por Segmento
    df_rec = df.groupby("segmento_cliente", as_index=False)["receita_total"].sum()
    fig2 = px.bar(df_rec, x="segmento_cliente", y="receita_total",
                  title="Receita por Segmento",
                  labels={"segmento_cliente": "Segmento", "receita_total": "Receita (R$)"})
    col_b.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    # Gráfico 3 — Top 10 Clientes
    df_top10 = df[df["ranking_receita"] <= 10].sort_values("ranking_receita")
    fig3 = px.bar(df_top10, x="receita_total", y="nome_cliente", orientation="h",
                  title="Top 10 Clientes",
                  labels={"receita_total": "Receita (R$)", "nome_cliente": "Cliente"})
    fig3.update_yaxes(autorange="reversed")
    col_c.plotly_chart(fig3, use_container_width=True)

    # Gráfico 4 — Clientes por Estado
    df_estado = df.groupby("estado", as_index=False).size().rename(columns={"size": "total"})
    df_estado = df_estado.sort_values("total", ascending=False)
    fig4 = px.bar(df_estado, x="estado", y="total",
                  title="Clientes por Estado",
                  labels={"estado": "Estado", "total": "Clientes"})
    col_d.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # Tabela detalhada
    segmentos = ["Todos", "VIP", "TOP_TIER", "REGULAR"]
    sel_seg = st.selectbox("Filtrar por segmento", segmentos)
    df_tabela = df if sel_seg == "Todos" else df[df["segmento_cliente"] == sel_seg]
    st.dataframe(df_tabela, use_container_width=True)


# ---------------------------------------------------------------------------
# Página: Pricing
# ---------------------------------------------------------------------------

def page_pricing():
    st.title("Pricing")

    df = run_query("SELECT * FROM public_gold_pricing.precos_competitividade")

    categorias = sorted(df["categoria"].unique())
    sel_cats = st.multiselect("Categorias", categorias, default=categorias)
    if sel_cats:
        df = df[df["categoria"].isin(sel_cats)]

    total_produtos = len(df)
    mais_caros = len(df[df["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"])
    mais_baratos = len(df[df["classificacao_preco"] == "MAIS_BARATO_QUE_TODOS"])
    dif_media = df["diferenca_percentual_vs_media"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Produtos Monitorados", fmt_int(total_produtos))
    c2.metric("Mais Caros que Todos", fmt_int(mais_caros))
    c3.metric("Mais Baratos que Todos", fmt_int(mais_baratos))
    c4.metric("Diferença Média vs Mercado", fmt_pct(dif_media))

    st.divider()

    col_a, col_b = st.columns(2)

    # Gráfico 1 — Posicionamento vs Concorrência
    df_class = df.groupby("classificacao_preco", as_index=False).size().rename(columns={"size": "total"})
    fig1 = px.pie(df_class, names="classificacao_preco", values="total",
                  title="Posicionamento de Preço vs Concorrência", hole=0.3)
    col_a.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2 — Competitividade por Categoria
    df_cat = df.groupby("categoria", as_index=False)["diferenca_percentual_vs_media"].mean()
    df_cat["cor"] = df_cat["diferenca_percentual_vs_media"].apply(
        lambda x: "Mais caro" if x > 0 else "Mais barato"
    )
    fig2 = px.bar(df_cat, x="categoria", y="diferenca_percentual_vs_media", color="cor",
                  color_discrete_map={"Mais caro": "#EF553B", "Mais barato": "#00CC96"},
                  title="Competitividade por Categoria",
                  labels={"categoria": "Categoria", "diferenca_percentual_vs_media": "Diferença % vs Média"})
    col_b.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3 — Competitividade × Volume de Vendas
    fig3 = px.scatter(df, x="diferenca_percentual_vs_media", y="quantidade_total",
                      color="classificacao_preco", size="receita_total",
                      hover_data=["nome_produto", "categoria"],
                      title="Competitividade × Volume de Vendas",
                      labels={
                          "diferenca_percentual_vs_media": "Diferença % vs Média",
                          "quantidade_total": "Quantidade Vendida",
                          "classificacao_preco": "Classificação",
                      })
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # Tabela de alertas
    st.subheader("Produtos em Alerta (mais caros que todos os concorrentes)")
    df_alerta = df[df["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"][
        ["produto_id", "nome_produto", "categoria", "nosso_preco",
         "preco_maximo_concorrentes", "diferenca_percentual_vs_media"]
    ]
    st.dataframe(df_alerta, use_container_width=True)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

st.sidebar.title("E-commerce Analytics")
pagina = st.sidebar.radio("Navegação", ["Vendas", "Clientes", "Pricing"])

if pagina == "Vendas":
    page_vendas()
elif pagina == "Clientes":
    page_clientes()
elif pagina == "Pricing":
    page_pricing()
