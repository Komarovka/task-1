import os
import re

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def build_engine():
    load_dotenv()
    
    # Проверка обязательных переменных
    for var in ["DB_USER", "DB_PASSWORD", "DB_HOST"]:
        if not os.getenv(var):
            raise ValueError(f"Missing environment variable: {var}")

    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "homeworks"),
    )
    return create_engine(url)


def load(df: pd.DataFrame, table: str) -> int:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", table):
        raise ValueError(f"bad table name: {table}")
    engine = build_engine()
    with engine.begin() as conn:
        # Внимание: if_exists="replace" удаляет старую таблицу и создаёт новую
        df.to_sql(table, conn, index=False, if_exists="replace")
        return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()