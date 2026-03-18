import subprocess
from pathlib import Path

PROJECT_ROOT = Path(".")

DOCS = [
    ".llm/init.md",
    ".llm/coding_rules.md",
    "docs/database.md",
    "docs/prd-dashboard.md",
]


def load_docs():

    context = ""

    for doc in DOCS:

        path = PROJECT_ROOT / doc

        if path.exists():
            context += f"\n\n# FILE: {doc}\n"
            context += path.read_text()

    return context


def ask_llm(prompt):

    result = subprocess.run(
        ["ollama", "run", "deepseek-coder", prompt],
        capture_output=True,
        text=True
    )

    return result.stdout


def generate_file(task):

    context = load_docs()

    full_prompt = f"""
{context}

TASK:
{task}
"""

    response = ask_llm(full_prompt)

    return response