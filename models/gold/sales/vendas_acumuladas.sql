WITH vendas_mensais AS (
    SELECT
        ano_venda,
        mes_venda,
        SUM(receita_total) AS receita_mensal,
        SUM(quantidade) AS quantidade_mensal,
        COUNT(DISTINCT id_venda) AS vendas_mensais
    FROM {{ ref('silver_vendas') }}
    GROUP BY 
        ano_venda, 
        mes_venda
)

SELECT
    ano_venda,
    mes_venda,
    receita_mensal,
    SUM(receita_mensal) OVER (ORDER BY ano_venda, mes_venda) AS receita_acumulada,
    quantidade_mensal,
    SUM(quantidade_mensal) OVER (ORDER BY ano_venda, mes_venda) AS quantidade_acumulada,
    vendas_mensais,
    SUM(vendas_mensais) OVER (ORDER BY ano_venda, mes_venda) AS total_vendas_acumuladas
FROM vendas_mensais
ORDER BY 
    ano_venda, 
    mes_venda
