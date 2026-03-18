import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = os.getenv("POSTGRES_URL")
        if not url:
            raise ValueError("POSTGRES_URL não configurado no .env")
        _engine = create_engine(url)
    return _engine


def execute_query(sql: str) -> pd.DataFrame:
    sql_stripped = sql.strip().upper()
    if not (sql_stripped.startswith("SELECT") or sql_stripped.startswith("WITH")):
        raise ValueError("Apenas queries SELECT ou WITH são permitidas.")

    engine = get_engine()
    with engine.connect() as conn:
        result = pd.read_sql(text(sql), conn)
    return result
