BASE_PROMPT = """
You are a senior Python engineer.

You are building a production analytics dashboard.

Read the project documentation before writing code.

Never invent database columns.
"""


def build_prompt(context, task):
    return f"""
{BASE_PROMPT}

PROJECT CONTEXT
{context}

TASK
{task}

Generate the code.
"""