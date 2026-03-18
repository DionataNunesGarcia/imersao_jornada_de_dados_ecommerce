from agent.agent import generate_file

task = """
Generate the file:

case-01-dashboard/app.py

Complete Streamlit dashboard with:

- vendas page
- clientes page
- pricing page
"""

code = generate_file(task)

print(code)

with open("case-01-dashboard/app.py", "w") as f:
    f.write(code)