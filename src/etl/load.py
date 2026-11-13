import os
import re

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def build_engine():
    load_dotenv()
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
        df.to_sql(table, conn, index=False, if_exists="replace")
        return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()