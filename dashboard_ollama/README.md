# Dia 4: Claude Code & Python | Jornada de Dados

Ultimo dia da imersao. Os dados estao prontos no banco. Agora o desafio e diferente: **como levar esses insights ate quem toma decisao?**

---

## A Situacao

Nos 3 dias anteriores voce construiu um pipeline completo:

| Dia | O que fez | Resultado |
| --- | --------- | --------- |
| Dia 1 - SQL | Entendeu o negocio com queries | Perguntas de negocio respondidas |
| Dia 2 - Python | Ingeriu dados de multiplas fontes | Dados no banco PostgreSQL |
| Dia 3 - dbt | Estruturou camadas Bronze/Silver/Gold | 3 Data Marts prontos para consumo |

O pipeline funciona. Os 3 Data Marts estao no banco:

```
public_gold_sales.vendas_temporais        --> Metricas de vendas por dia/hora
public_gold_cs.clientes_segmentacao       --> Segmentacao VIP/TOP_TIER/REGULAR
public_gold_pricing.precos_competitividade --> Posicionamento vs concorrencia
```

**Mas nenhum diretor acessa o banco de dados.**

---

## O Problema Real

Tres diretores precisam de dados todos os dias. Cada um tem uma dor diferente:

### Diretor Comercial (Vendas)

> "Preciso ver a receita de ontem antes da reuniao das 9h.
> Quero saber se estamos acima ou abaixo da meta.
> Quero ver o ticket medio e quais dias da semana vendem mais."

**Dado que ele precisa:** `vendas_temporais`
**Como ele consome hoje:** Pede pro analista. Demora 2 dias.

### Diretora de Customer Success (Clientes)

> "Preciso saber quantos clientes VIP temos e quanto eles representam.
> Quero ver quem esta comprando menos para ligar antes que cancele.
> Preciso da distribuicao por estado para planejar a equipe regional."

**Dado que ela precisa:** `clientes_segmentacao`
**Como ela consome hoje:** Recebe uma planilha por email. Toda segunda-feira. Ja desatualizada.

### Diretor de Pricing (Precos)

> "Preciso saber quantos produtos estao mais caros que a concorrencia.
> Quero ver quais categorias estao fora do mercado.
> Preciso de alerta quando um produto fica mais caro que todos os concorrentes."

**Dado que ele precisa:** `precos_competitividade`
**Como ele consome hoje:** Nao consome. Ninguem faz essa analise.

---

## A Solucao: 2 Projetos em 30 Minutos

Voce vai usar **Claude Code + Python** para resolver os 3 diretores de uma vez:

```
Case 1: Dashboard Streamlit    --> Self-service para os 3 diretores
Case 2: Agente de Relatorios   --> Envia insights as 8h da manha
```

---

## Pre-requisitos

Antes de comecar, voce precisa ter:

- [ ] Claude Code CLI instalado (`claude --version`)
- [ ] Banco Supabase rodando com os 3 Data Marts gold (aula-03)
- [ ] Connection string do banco PostgreSQL
- [ ] Chave de API da Anthropic (para o Case 2)

Detalhes de instalacao no **[GUIA_INSTALACAO.md](./GUIA_INSTALACAO.md)**.

---

## Passo a Passo

### Passo 1: Criar a estrutura de pastas

Crie a pasta do Case 1 com a pasta `.llm` dentro. A pasta `.llm` e onde voce guarda o **contexto tecnico** que o Claude Code vai ler antes de gerar codigo.

```bash
mkdir -p case-01-dashboard/.llm
```

### Passo 2: Copiar os arquivos de contexto para o Case 1

O Claude Code precisa de 2 coisas para gerar codigo bom: **o que existe no banco** (database.md) e **o que voce quer construir** (prd.md).

```bash
cp database.md case-01-dashboard/.llm/database.md
cp prd-dashboard.md case-01-dashboard/.llm/prd.md
```

A pasta fica assim:

```
case-01-dashboard/
└── .llm/
    ├── database.md    # Catalogo dos 3 Data Marts (schemas, colunas, sample data)
    └── prd.md         # O que o dashboard deve ter (paginas, graficos, KPIs)
```

### Passo 3: Entrar na pasta e iniciar o Claude Code

```bash
cd case-01-dashboard
claude --dangerously-skip-permissions
```

O flag `--dangerously-skip-permissions` da acesso total ao Claude Code: ele pode criar arquivos, instalar dependencias e executar comandos sem pedir confirmacao a cada passo. Isso acelera o fluxo na aula.

O Claude Code abre um terminal interativo. Ele ja consegue ler os arquivos da pasta `.llm/` automaticamente.

### Passo 4: Rodar o /init e criar o CLAUDE.md

Dentro do Claude Code, rode:

```
/init
```

O `/init` cria um arquivo `CLAUDE.md` na raiz do projeto. Esse arquivo e o **manual do projeto para o Claude Code**. Ele funciona como uma `system message` persistente: toda vez que voce abrir o Claude Code nessa pasta, ele le o `CLAUDE.md` primeiro.

**O que colocar no CLAUDE.md:**

O `/init` vai gerar um arquivo base. Edite para incluir:

```markdown
# Dashboard E-commerce

## Contexto
Dashboard Streamlit para 3 diretores de um e-commerce.
Conecta no banco PostgreSQL (Supabase) e consome 3 Data Marts gold.

## Stack
- Python 3.10+
- Streamlit
- Plotly (graficos)
- psycopg2-binary (conexao PostgreSQL)
- python-dotenv

## Banco de Dados
Connection string via variavel de ambiente POSTGRES_URL no arquivo .env.
Ver .llm/database.md para schemas completos das tabelas.

## Regras
- Nao commitar .env com credenciais
- Formatar valores monetarios em reais (R$)
- Usar plotly para todos os graficos (nao matplotlib)
- Layout wide no Streamlit
```

**Por que o CLAUDE.md importa?**

Sem ele, toda vez que voce abre o Claude Code, precisa explicar o projeto do zero. Com ele, o Claude Code ja sabe:
- Qual e o projeto
- Qual stack usar
- Onde esta o banco
- Quais regras seguir

E como um onboarding automatico.

### Passo 5: Pedir para o Claude Code construir o dashboard

Agora que o contexto esta pronto, peca:

```
Leia o .llm/prd.md e o .llm/database.md e construa o dashboard completo.
```

O Claude Code vai:
1. Ler o PRD (o que construir)
2. Ler o database.md (quais tabelas e colunas existem)
3. Gerar o `app.py`, `requirements.txt` e `.env.example`

**Valide o resultado.** Se algo nao ficou como voce queria:

```
Mude o grafico de receita para barras horizontais.
Adicione um filtro de mes na pagina de Vendas.
O ticket medio esta errado, deve ser receita / vendas.
```

Iterar e parte do processo. O PRD e o ponto de partida, nao o resultado final.

### Passo 5.1: Usar Skills para melhorar o visual

O Claude Code tem um sistema de **Skills** — instrucoes especializadas que voce pode instalar para mudar o comportamento dele em tarefas especificas.

Para dashboards e interfaces, existe a skill **frontend-design** que faz o Claude Code gerar interfaces com design profissional em vez do visual padrao generico.

**Como instalar a skill:**

1. Baixe o arquivo da skill:

```bash
mkdir -p .claude/skills
curl -o .claude/skills/frontend-design.md https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md
```

2. Pronto. O Claude Code le automaticamente os arquivos em `.claude/skills/` e aplica as instrucoes.

**O que a skill frontend-design muda:**

| Aspecto | Sem a skill | Com a skill |
| ------- | ----------- | ----------- |
| Tipografia | Fontes padrao (Arial, Inter) | Fontes distintivas com pareamento display + body |
| Cores | Cinza generico | Paleta coesa com CSS variables e acentos fortes |
| Layout | Colunas basicas | Composicao com assimetria e hierarquia visual |
| Motion | Estatico | Animacoes em momentos de impacto |
| Resultado | "Parece um template" | "Parece que um designer fez" |

**Exemplo pratico no dashboard:**

Depois de instalar a skill, peca:

```
Refatore o visual do dashboard com um design profissional.
Use uma paleta de cores corporativa, tipografia moderna
e cards com sombra para os KPIs.
```

A skill faz o Claude Code pensar em design antes de codar — ele vai considerar proposito, tom e diferenciacao visual em vez de aplicar o visual padrao do Streamlit.

**Mais skills disponiveis:**

O repositorio oficial de skills fica em `github.com/anthropics/skills`. Voce pode explorar e instalar outras skills conforme a necessidade do projeto.

### Passo 6: Testar o dashboard

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Criar .env com a connection string
cp .env.example .env
# Editar .env com suas credenciais

# Rodar
streamlit run app.py
```

O dashboard abre em `http://localhost:8501`. Verifique:
- [ ] Pagina de Vendas: KPIs e 3 graficos com dados reais
- [ ] Pagina de Clientes: segmentacao e top 10
- [ ] Pagina de Pricing: classificacao e alertas

---

### Passo 7: Criar a estrutura do Case 2

Repita o processo para o Agente de Relatorios:

```bash
cd ..
mkdir -p case-02-agente/.llm
cp database.md case-02-agente/.llm/database.md
cp prd-agente-relatorios.md case-02-agente/.llm/prd.md
```

### Passo 8: Iniciar o Claude Code no Case 2

```bash
cd case-02-agente
claude --dangerously-skip-permissions
```

### Passo 9: Rodar o /init e criar o CLAUDE.md

```
/init
```

Edite o `CLAUDE.md` gerado:

```markdown
# Agente de Relatorios Diarios

## Contexto
Script Python que consulta 3 Data Marts gold no PostgreSQL,
envia os dados para a API do Claude e gera um relatorio executivo
diario para 3 diretores (Comercial, CS, Pricing).

## Stack
- Python 3.10+
- anthropic (SDK)
- psycopg2-binary
- pandas
- python-dotenv

## Banco de Dados
Connection string via POSTGRES_URL no .env.
Ver .llm/database.md para schemas completos.

## API
Chave da Anthropic via ANTHROPIC_API_KEY no .env.
Usar modelo claude-sonnet-4-20250514 para custo baixo.

## Regras
- Nao commitar .env com credenciais
- Tratar erro de conexao antes de chamar a API
- Salvar relatorio como .md com data no nome
- Logging com timestamps em cada etapa
```

### Passo 10: Pedir para o Claude Code construir o agente

```
Leia o .llm/prd.md e o .llm/database.md e construa o agente de relatorios completo.
```

### Passo 11: Testar o agente

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Criar .env
cp .env.example .env
# Editar .env com credenciais

# Rodar
python agente.py
```

O relatorio deve aparecer no terminal e ser salvo como `relatorio_YYYY-MM-DD.md`.

---

## Estrutura Final

Ao final dos 2 cases, a pasta fica assim:

```
aula-04-claude-code/
├── README.md                        # Este arquivo (passo a passo)
├── GUIA_INSTALACAO.md               # Instalacao do Claude Code e dependencias
├── database.md                      # Catalogo dos 3 Data Marts gold
├── prd-dashboard.md                 # PRD original do Case 1
├── prd-agente-relatorios.md         # PRD original do Case 2
│
├── case-01-dashboard/               # Case 1: Dashboard
│   ├── CLAUDE.md                    # Contexto do projeto para o Claude Code
│   ├── .llm/
│   │   ├── database.md              # Copia do catalogo de dados
│   │   └── prd.md                   # PRD do dashboard
│   ├── app.py                       # App Streamlit (gerado pelo Claude Code)
│   ├── requirements.txt             # Dependencias
│   ├── .env.example                 # Template de variaveis
│   └── .env                         # Credenciais reais (nao commitar)
│
└── case-02-agente/                  # Case 2: Agente de Relatorios
    ├── CLAUDE.md                    # Contexto do projeto para o Claude Code
    ├── .llm/
    │   ├── database.md              # Copia do catalogo de dados
    │   └── prd.md                   # PRD do agente
    ├── agente.py                    # Script do agente (gerado pelo Claude Code)
    ├── requirements.txt             # Dependencias
    ├── .env.example                 # Template de variaveis
    └── .env                         # Credenciais reais (nao commitar)
```

---

## Conceitos que Voce Aprende

### 1. A Pasta .llm/ (Contexto para IA)

A pasta `.llm/` e uma convencao para guardar arquivos que servem de **contexto tecnico para agentes de IA**. Nao e codigo, nao e config — e documentacao que a IA le antes de trabalhar.

| Arquivo | Funcao |
| ------- | ------ |
| `.llm/database.md` | O que existe no banco (schemas, colunas, regras) |
| `.llm/prd.md` | O que voce quer construir (requisitos, telas, comportamento) |

**Analogia:** Se o Claude Code e um desenvolvedor junior que acabou de entrar na empresa, a pasta `.llm/` e o onboarding escrito. Quanto melhor o onboarding, menos perguntas ele faz e melhor o codigo que ele entrega.

### 2. O CLAUDE.md (System Message do Projeto)

O `CLAUDE.md` e um arquivo especial que o Claude Code le **automaticamente** toda vez que abre na pasta. Funciona como uma system message persistente.

| Aspecto | Sem CLAUDE.md | Com CLAUDE.md |
| ------- | ------------- | ------------- |
| Primeira mensagem | "Este e um projeto Streamlit que..." | Ja sabe o projeto |
| Stack | Pode escolher matplotlib | Sabe que deve usar plotly |
| Banco | "Qual e a connection string?" | Sabe que esta no .env |
| Erros repetidos | Comete os mesmos | Le as regras e evita |

**O /init gera a estrutura base.** Voce edita com as regras especificas do projeto.

### 3. PRD como Interface Humano-IA

O PRD (Product Requirements Document) nao e um documento burocrtico. E a **instrucao precisa** que voce da para o Claude Code. A diferenca entre um resultado bom e ruim esta na qualidade do PRD:

**PRD vago → resultado generico:**
```
Faz um dashboard de vendas.
```

**PRD especifico → resultado preciso:**
```
Pagina de Vendas com 4 KPIs (receita total, total vendas, ticket medio,
clientes unicos) em st.columns(4), grafico de receita diaria em px.line,
e grafico de vendas por hora em px.bar. Dados da tabela
public_gold_sales.vendas_temporais.
```

### 4. Data Products

Dashboard e agente de relatorios sao **produtos de dados**. O pipeline (SQL + Python + dbt) so tem valor quando alguem consome o resultado. Hoje voce fecha o ciclo:

```
Dados Brutos --> Pipeline --> Data Marts --> Produtos de Dados --> Decisao
   Dia 2         Dia 3        Dia 3            Dia 4              ✓
```

---

## Resultado Final da Imersao

Ao final dos 4 dias, voce construiu:

| Camada | Ferramenta | Entrega |
| ------ | ---------- | ------- |
| Analise | SQL | 21 queries respondendo perguntas de negocio |
| Ingestao | Python | Scripts que coletam dados de CSVs, APIs e bancos |
| Transformacao | dbt | 11 modelos em arquitetura Medalhao (Bronze/Silver/Gold) |
| Consumo | Claude Code + Python | Dashboard + Agente de Relatorios para 3 diretores |

**Isso e um projeto de dados completo. Do dado bruto ate a decisao.**