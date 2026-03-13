# Projeto dbt: E-commerce Analytics (Jornada de Dados)

> **Nota:** Este projeto foi desenvolvido durante uma imersão do curso da [Jornada de Dados](https://www.youtube.com/@JornadaDeDados).

Este projeto implementa uma camada analítica moderna utilizando **dbt (data build tool)** sobre um banco de dados relacional hospedado no **Supabase** (PostgreSQL). O objetivo é transformar dados brutos transacionais de um e-commerce em modelos padronizados, testados e prontos para análise de negócios (BI, relatórios estruturados e métricas).

## 🏗️ Arquitetura de Dados (Medalhão)

O projeto segue rigidamente a **Arquitetura Medalhão**, dividindo os pipelines de processamento de dados em três camadas lógicas bem definidas:

1. **Bronze (Raw / Pass-through)**: Materializada como `views`. São espelhos das tabelas originais (`raw`) que estão armazenadas no banco de dados. Servem como camada restrita de leitura direta, sem transformações ativas de regras de negócio; atuam como um contrato confiável de dados originais.
2. **Silver (Limpeza e Padronização)**: Materializada como `tables`. Contêm as regras estruturais, tipagem, padronizações iniciais e junção de colunas calculadas em nível de linha, estendendo a tabela bronze equivalente de formato 1:1. Não possuem agregações complexas (`GROUP BY`) nem perdem a granularidade dos eventos.
3. **Gold (Business / Analytics)**: Materializada como `tables`. Visões agregadas do negócio distribuídas em Data Marts específicos (Sales, Customer Success, Pricing). Essas tabelas combinam múltiplos modelos da Silver para responder à perguntas diretas de negócios através de métricas sumarizadas.

### 🗂 Estrutura dos Modelos

```text
models/
├── _sources.yml                  # Mapeamento do catálogo das tabelas brutas do Supabase (schema public)
├── bronze/                       # Camada Bronze 
│   ├── bronze_clientes.sql
│   ├── bronze_preco_competidores.sql
│   ├── bronze_produtos.sql
│   └── bronze_vendas.sql
├── silver/                       # Camada Silver 
│   ├── silver_clientes.sql
│   ├── silver_preco_competidores.sql
│   ├── silver_produtos.sql
│   └── silver_vendas.sql
└── gold/                         # Camada Gold (Data Marts)
    ├── customer_success/         # Mart de Clientes / CRM
    │   └── clientes_segmentacao.sql
    ├── pricing/                  # Mart de Inteligência de Preços
    │   └── precos_competitividade.sql
    └── sales/                    # Mart de Vendas e Transacional
        ├── vendas_acumuladas.sql
        └── vendas_temporais.sql
```

---

## ⚙️ Pré-requisitos

Para trabalhar com este projeto e executar as automações localmente, você necessitará de:
- **Python 3.8+** instalado.
- **Git** para versionamento.
- Uma conta e um projeto criado no **Supabase** (para hospedagem gratuíta de PostgreSQL).
- As credenciais de conexão do seu banco Supabase (`Host`, `Port`, `Database`, `User`, `Password`).

---

## 🚀 Passo a Passo para Configuração e Execução

### 1. Clonar e Inicializar o Ambiente
Abra seu terminal e acesse a pasta desejada:
```bash
# (Opcional) Cria e ativa um ambiente Python virtual para o dbt
python -m venv venv

# Ativando no Linux/Mac
source venv/bin/activate 
# Ativando no Windows
# venv\Scripts\activate 

# Instala o dbt-core e o adapter especifico do PostgreSQL (para rodar via Supabase)
pip install dbt-core dbt-postgres
```

### 2. Configurando as credenciais do Supabase (`profiles.yml`)

O dbt realiza o gerenciamento de configurações de banco de dados em um arquivo universal chamado `profiles.yml` que não é versionado junto ao código. 
Normalmente sua máquina o localiza na pasta oculta do seu usuário raiz (`~/.dbt/`).

1. Se não existir, crie um arquivo chamado `profiles.yml` dentro de `~/.dbt/`.
2. Adicione as instruções de acesso do seu projeto configurando um target com o nome referenciado (`ecommerce`):

```yaml
ecommerce:
  target: dev
  outputs:
    dev:
      type: postgres
      host: aws-0-sa-east-1.pooler.supabase.com # Verifique no config do seu Supabase
      user: postgres.seu_id_do_projeto          # Usuário
      password: sua_senha_root                  # Senha segura do banco
      port: 5432
      dbname: postgres                          # Nome do banco padrao
      schema: public                            # Schema onde se encontra o Raw e ocorrera a criação das tabelas dbt
      threads: 4
      keepalives_idle: 0
```
> *Lembrete: Você encontra esses dados de acesso acessando as 'Project Settings' > 'Database' no painel de controle do seu projeto no portal do Supabase.*

Para confirmar que a ponte entre o dbt e o Supabase está livre, entre no diretório do seu dbt_project e solicite um teste:
```bash
# Entre na raiz do projeto (onde está o dbt_project.yml)
cd eccomerce 

# Verifique o adapter do BD
dbt debug
```
*(Espera-se receber a mensagem gráfica em verde: "All checks passed!")*

### 3. Rodando o Pipeline (Materializando as Tabelas)

Para iniciar o fluxo de ETL real, materializando as tabelas no Postgres através das diretrizes do DBT e da DAG inter-modelos montada:

```bash
# Executa todos os grafos do seu projeto:
dbt run
```

O comando se encarregará de criar os `schemas` descritos (`bronze`, `silver`, `gold_cs`, `gold_pricing`, `gold_sales`) e embutir perfeitamente todas suas estruturas `view`/`table`.

**Dicas de Execuções mais Granulares:**
- Para rodar apenas todos os modelos da camada `silver`:
  ```bash
  dbt run --select path:models/silver
  ```
- Para rodar apenas um Data Mart em específico (Ex: Pricing) e atualizar sua tabela mãe:
  ```bash
  dbt run --select precos_competitividade+
  ```

### 4. Gerando e Lendo a Documentação Dinâmica

O grande poder do dbt está em conseguir transformar o schema mapeado (descrições feitas em `yml`) somado à leitura do código SQL num portal web estático, demonstrando a linhagem e rastreamento dos dados (`DAG`).

Para computar/atualizar a documentação:
```bash
dbt docs generate
```

E para subir um host local exibindo o site interativo no seu navegador:
```bash
dbt docs serve
```

---
**Tech Stack**: Banco de Dados PostgreSQL (Supabase) | Modelador Data Build Tool (dbt)
