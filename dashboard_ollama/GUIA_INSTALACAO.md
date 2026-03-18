# Guia de Instalacao - Claude Code

Tudo que voce precisa instalar para a Aula 04.

---

## 1. Node.js (pre-requisito)

Claude Code roda em Node.js 18+.

**Verificar se ja tem:**

```bash
node --version
```

Se retornar `v18.x` ou superior, pule para o passo 2.

**Instalar Node.js:**

```bash
# Mac (Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows (baixar instalador)
# https://nodejs.org/en/download
```

---

## 2. Claude Code (CLI)

```bash
npm install -g @anthropic-ai/claude-code
```

**Verificar instalacao:**

```bash
claude --version
```

**Primeiro uso:**

```bash
claude
```

Na primeira execucao, o Claude Code vai pedir para autenticar. Siga as instrucoes no terminal para conectar sua conta Anthropic.

---

## 3. Chave de API da Anthropic

Necessaria para o Case 2 (Agente de Relatorios).

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Crie uma conta (se ainda nao tem)
3. Va em **API Keys** e crie uma nova chave
4. Copie a chave (formato: `sk-ant-...`)
5. Guarde em local seguro — voce vai usar no `.env`

---

## 4. Python 3.10+

**Verificar se ja tem:**

```bash
python3 --version
```

**Instalar Python:**

```bash
# Mac (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# Windows (baixar instalador)
# https://www.python.org/downloads/
```

---

## 5. Banco de Dados (Supabase)

Voce ja deve ter o banco rodando desde a Aula 03 (dbt).

**Verificar se os Data Marts gold existem:**

Acesse o Supabase Dashboard → SQL Editor e rode:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema LIKE 'public_gold%'
ORDER BY table_schema, table_name;
```

Deve retornar 3 tabelas:

| Schema | Tabela |
| ------ | ------ |
| public_gold_sales | vendas_temporais |
| public_gold_cs | clientes_segmentacao |
| public_gold_pricing | precos_competitividade |

Se nao retornar, volte na Aula 03 e rode `dbt run`.

---

## 6. Credenciais do Banco

Voce vai precisar da connection string do Supabase.

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. Va em **Settings** → **Database**
4. Copie a **Connection string** (URI format)
5. Substitua `[YOUR-PASSWORD]` pela senha do projeto

O formato e:

```
postgresql://postgres.xxxxx:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

---

## Checklist Final

Antes de comecar a aula, confirme:

- [ ] `node --version` retorna 18+
- [ ] `claude --version` funciona
- [ ] `python3 --version` retorna 3.10+
- [ ] Conta na Anthropic com API Key gerada
- [ ] Banco Supabase rodando com os 3 Data Marts gold
- [ ] Connection string do banco em maos

---

## Troubleshooting

**"command not found: claude"**

```bash
# Verificar se npm global esta no PATH
npm config get prefix
# Adicionar ao PATH se necessario (Mac/Linux):
export PATH="$(npm config get prefix)/bin:$PATH"
```

**"Permission denied" ao instalar global**

```bash
# Mac/Linux - usar sudo
sudo npm install -g @anthropic-ai/claude-code

# Ou configurar npm para instalar sem sudo
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

**"Could not connect to database"**

- Verifique se a senha esta correta na connection string
- Verifique se o IP esta liberado no Supabase (Settings → Database → Network)
- Teste a conexao: `psql "sua_connection_string"`

**"ANTHROPIC_API_KEY not set"**

```bash
# Verificar se a variavel esta no .env
cat .env | grep ANTHROPIC

# Ou exportar diretamente
export ANTHROPIC_API_KEY=sk-ant-sua-chave
```