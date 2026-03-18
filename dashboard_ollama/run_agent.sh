#!/bin/bash

echo "Loading project context..."

CONTEXT=$(cat .llm/INIT.md)
PRD=$(cat prd-dashboard.md)
DB=$(cat database.md)

PROMPT="$CONTEXT

# PRD
$PRD

# Database Documentation
$DB

Agora gere o código completo do dashboard Streamlit conforme o PRD."

ollama run deepseek-coder "$PROMPT"

from agent.agent import generate_file

task = "Write a simple Python script that prints 'Hello Dashboard'"

code = generate_file(task)

print(code)