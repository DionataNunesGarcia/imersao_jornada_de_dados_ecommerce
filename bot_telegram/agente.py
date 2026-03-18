import os
import sys
import json
import logging
import urllib.request
import urllib.parse
from datetime import date, datetime
from dotenv import load_dotenv
import anthropic
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from db import execute_query

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

MODEL = "claude-sonnet-4-20250514"

SCHEMA_CONTEXT = """
## Schemas dos Data Marts Gold

### public_gold_sales.vendas_temporais
Granularidade: 1 linha por data_venda + hora_venda
Colunas: data_venda (DATE), ano_venda (INT), mes_venda (INT), dia_venda (INT),
         dia_semana_nome (VARCHAR), hora_venda (INT), receita_total (NUMERIC),
         quantidade_total (INT), total_vendas (INT), total_clientes_unicos (INT),
         ticket_medio (NUMERIC)

### public_gold_cs.clientes_segmentacao
Granularidade: 1 linha por cliente
Colunas: cliente_id (VARCHAR), nome_cliente (VARCHAR), estado (VARCHAR(2)),
         receita_total (NUMERIC), total_compras (INT), ticket_medio (NUMERIC),
         primeira_compra (DATE), ultima_compra (DATE),
         segmento_cliente (VARCHAR: VIP|TOP_TIER|REGULAR), ranking_receita (INT)
Segmentação: VIP >= R$10.000 | TOP_TIER >= R$5.000 | REGULAR < R$5.000

### public_gold_pricing.precos_competitividade
Granularidade: 1 linha por produto (com dados de concorrentes)
Colunas: produto_id (VARCHAR), nome_produto (VARCHAR), categoria (VARCHAR),
         marca (VARCHAR), nosso_preco (NUMERIC), preco_medio_concorrentes (NUMERIC),
         preco_minimo_concorrentes (NUMERIC), preco_maximo_concorrentes (NUMERIC),
         total_concorrentes (INT), diferenca_percentual_vs_media (NUMERIC),
         diferenca_percentual_vs_minimo (NUMERIC),
         classificacao_preco (VARCHAR: MAIS_CARO_QUE_TODOS|ACIMA_DA_MEDIA|NA_MEDIA|ABAIXO_DA_MEDIA|MAIS_BARATO_QUE_TODOS),
         receita_total (NUMERIC), quantidade_total (INT)
Concorrentes: Mercado Livre, Amazon, Shopee, Magalu
Categorias: Eletrônicos, Casa, Moda, Games, Cozinha, Beleza, Acessórios
"""

TOOL_EXECUTAR_SQL = {
    "name": "executar_sql",
    "description": "Executa query SQL SELECT no banco PostgreSQL do e-commerce.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "Query SQL SELECT para executar."
            }
        },
        "required": ["sql"]
    }
}


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def _log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def salvar_chat_id(novo_chat_id: str):
    novo_chat_id = str(novo_chat_id)
    if os.getenv("CHAT_ID", "") == novo_chat_id:
        return

    env_path = ".env"
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        linhas = []

    nova_linha = f"CHAT_ID={novo_chat_id}\n"
    encontrado = False
    for i, linha in enumerate(linhas):
        if linha.startswith("CHAT_ID="):
            linhas[i] = nova_linha
            encontrado = True
            break

    if not encontrado:
        linhas.append(nova_linha)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(linhas)

    os.environ["CHAT_ID"] = novo_chat_id
    _log(f"CHAT_ID={novo_chat_id} salvo no .env")


# ---------------------------------------------------------------------------
# Agente de chat (tool use)
# ---------------------------------------------------------------------------

def chat(pergunta: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    system_prompt = (
        "Você é um analista de dados de um e-commerce brasileiro.\n"
        "Responda perguntas usando os dados do banco PostgreSQL.\n"
        "Use a ferramenta executar_sql para consultar os dados necessários.\n"
        "Formate valores monetários em R$. Responda em português.\n"
        "Seja conciso e direto.\n\n"
        + SCHEMA_CONTEXT
    )

    messages = [{"role": "user", "content": pergunta}]

    for _ in range(10):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=[TOOL_EXECUTAR_SQL],
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Sem resposta gerada."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use" and block.name == "executar_sql":
                    try:
                        df = execute_query(block.input.get("sql", ""))
                        resultado = df.to_markdown(index=False) if not df.empty else "Nenhum resultado encontrado."
                    except Exception as e:
                        resultado = f"Erro ao executar SQL: {e}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": resultado,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Limite de iterações atingido. Tente reformular a pergunta."


# ---------------------------------------------------------------------------
# Relatório executivo
# ---------------------------------------------------------------------------

def gerar_relatorio() -> str:
    _log("Iniciando geração do relatório...")

    queries = {
        "vendas": """
            SELECT data_venda, dia_semana_nome,
                SUM(receita_total) AS receita,
                SUM(total_vendas) AS vendas,
                SUM(total_clientes_unicos) AS clientes,
                AVG(ticket_medio) AS ticket_medio
            FROM public_gold_sales.vendas_temporais
            GROUP BY data_venda, dia_semana_nome
            ORDER BY data_venda DESC
            LIMIT 7
        """,
        "clientes": """
            SELECT segmento_cliente,
                COUNT(*) AS total_clientes,
                SUM(receita_total) AS receita_total,
                AVG(ticket_medio) AS ticket_medio_avg,
                AVG(total_compras) AS compras_avg
            FROM public_gold_cs.clientes_segmentacao
            GROUP BY segmento_cliente
            ORDER BY receita_total DESC
        """,
        "pricing": """
            SELECT classificacao_preco,
                COUNT(*) AS total_produtos,
                AVG(diferenca_percentual_vs_media) AS dif_media_pct,
                SUM(receita_total) AS receita_impactada
            FROM public_gold_pricing.precos_competitividade
            GROUP BY classificacao_preco
            ORDER BY total_produtos DESC
        """,
        "produtos_criticos": """
            SELECT nome_produto, categoria, nosso_preco,
                preco_medio_concorrentes,
                diferenca_percentual_vs_media,
                receita_total
            FROM public_gold_pricing.precos_competitividade
            WHERE classificacao_preco = 'MAIS_CARO_QUE_TODOS'
            ORDER BY diferenca_percentual_vs_media DESC
            LIMIT 10
        """,
    }

    dados = {}
    for nome, sql in queries.items():
        _log(f"Consultando {nome}...")
        try:
            dados[nome] = execute_query(sql)
        except Exception as e:
            _log(f"Erro ao consultar {nome}: {e}")
            dados[nome] = None

    _log("Enviando para Claude API...")

    partes = []
    for nome, df in dados.items():
        titulo = nome.replace("_", " ").title()
        if df is not None and not df.empty:
            partes.append(f"## {titulo}\n{df.to_markdown(index=False)}")
        else:
            partes.append(f"## {titulo}\nDados indisponíveis.")

    user_prompt = (
        "Gere o relatório diário com base nos dados abaixo.\n\n"
        + "\n\n".join(partes)
        + "\n\nGere o relatório com 3 seções:\n"
        "1. Comercial (para o Diretor Comercial)\n"
        "2. Customer Success (para a Diretora de CS)\n"
        "3. Pricing (para o Diretor de Pricing)\n\n"
        "Comece com um resumo executivo de 3 linhas antes das seções."
    )

    system_prompt = (
        "Você é um analista de dados senior de um e-commerce.\n"
        "Sua função é gerar um relatório executivo diário para 3 diretores.\n"
        "Cada diretor tem necessidades diferentes:\n\n"
        "1. Diretor Comercial: receita, vendas, ticket médio e tendências.\n"
        "2. Diretora de Customer Success: segmentação de clientes, VIPs e riscos.\n"
        "3. Diretor de Pricing: posicionamento de preço vs concorrência e alertas.\n\n"
        "Regras do relatório:\n"
        "- Seja direto e acionável. Cada insight deve sugerir uma ação.\n"
        "- Use números reais dos dados fornecidos.\n"
        "- Formate valores monetários em reais (R$).\n"
        "- Destaque alertas críticos no início.\n"
        "- O relatório deve ter no máximo 1 página por diretor.\n"
        "- Use formato Markdown."
    )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        relatorio = response.content[0].text
    except Exception as e:
        _log(f"Erro na API Claude: {e}. Usando dados brutos como fallback.")
        relatorio = (
            f"# Relatório Diário - E-commerce\nData: {date.today().strftime('%d/%m/%Y')}\n\n"
            + "\n\n".join(partes)
        )

    nome_arquivo = f"relatorio_{date.today().isoformat()}.md"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)
    _log(f"Relatório salvo em: {nome_arquivo}")

    return relatorio


# ---------------------------------------------------------------------------
# Envio direto via API HTTP do Telegram (sem bot rodando)
# ---------------------------------------------------------------------------

def enviar_telegram(texto: str, chat_id: str = None):
    if chat_id is None:
        chat_id = os.getenv("CHAT_ID")

    if not chat_id:
        _log("CHAT_ID não configurado. Inicie o bot e envie /start primeiro.")
        return

    token = os.getenv("TELEGRAM")
    if not token:
        _log("TELEGRAM token não configurado no .env")
        return

    for parte in [texto[i:i + 4096] for i in range(0, len(texto), 4096)]:
        _enviar_parte(token, chat_id, parte)


def _enviar_parte(token: str, chat_id: str, texto: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    for parse_mode in ["Markdown", None]:
        payload = {"chat_id": chat_id, "text": texto}
        if parse_mode:
            payload["parse_mode"] = parse_mode

        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if json.loads(resp.read().decode()).get("ok"):
                    _log(f"Mensagem enviada para chat_id={chat_id}")
                    return
        except Exception as e:
            if parse_mode == "Markdown":
                _log(f"Falha com Markdown, tentando texto puro: {e}")
            else:
                _log(f"Erro ao enviar mensagem: {e}")


# ---------------------------------------------------------------------------
# Handlers do bot Telegram
# ---------------------------------------------------------------------------

async def _handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salvar_chat_id(update.message.chat_id)
    await update.message.reply_text(
        "Olá! Sou o agente de dados do e-commerce.\n\n"
        "Você pode:\n"
        "• Enviar qualquer pergunta sobre vendas, clientes ou preços\n"
        "• Usar /relatorio para gerar o relatório executivo diário"
    )


async def _handler_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salvar_chat_id(update.message.chat_id)
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    try:
        relatorio = gerar_relatorio()
    except Exception as e:
        await update.message.reply_text(f"Erro ao gerar relatório: {e}")
        return

    for parte in [relatorio[i:i + 4096] for i in range(0, len(relatorio), 4096)]:
        try:
            await update.message.reply_text(parte, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(parte)


async def _handler_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salvar_chat_id(update.message.chat_id)
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    try:
        resposta = chat(update.message.text)
    except Exception as e:
        resposta = f"Erro ao processar pergunta: {e}"

    for parte in [resposta[i:i + 4096] for i in range(0, len(resposta), 4096)]:
        try:
            await update.message.reply_text(parte, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(parte)


# ---------------------------------------------------------------------------
# Ponto de entrada
#
# python agente.py            → sobe o bot em modo polling (uso normal)
# python agente.py --relatorio → gera relatório e envia via API HTTP (cron)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--relatorio" in sys.argv:
        relatorio = gerar_relatorio()
        print(relatorio)
        enviar_telegram(relatorio)
    else:
        token = os.getenv("TELEGRAM")
        if not token:
            raise ValueError("TELEGRAM token não configurado no .env")

        _log("Iniciando bot Telegram...")
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", _handler_start))
        app.add_handler(CommandHandler("relatorio", _handler_relatorio))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handler_mensagem))
        _log("Bot rodando! Ctrl+C para parar.")
        app.run_polling()
