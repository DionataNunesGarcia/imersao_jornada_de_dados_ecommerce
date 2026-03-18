import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("POSTGRES_URL"))

df = pd.read_sql("SELECT * FROM public_gold_sales.vendas_temporais LIMIT 5", conn)

print(df.head())