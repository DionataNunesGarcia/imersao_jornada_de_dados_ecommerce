SELECT
    id_cliente,
    nome_cliente,
    estado,
    pais,
    data_cadastro
FROM {{ ref('bronze_clientes') }}
