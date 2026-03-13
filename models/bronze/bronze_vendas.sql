select 
    id_venda,
    data_venda,
    id_cliente,
    id_produto,
    canal_venda,
    quantidade,
    preco_unitario
from {{ source('raw', 'vendas') }}