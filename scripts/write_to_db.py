import os
import sys
import re
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "homeworks")
TABLE_NAME = os.getenv("TABLE_NAME", "komarovka")
DATA_PATH = os.getenv("DATA_PATH", "data/SC_expression.parquet")

REQUIRED_ROWS = 100


def main():
    for var in ["DB_USER", "DB_PASSWORD", "DB_HOST"]:
        if not os.getenv(var):
            print(f"Missing env var: {var}")
            sys.exit(1)

    if not re.fullmatch(r"[a-z_][a-z0-9_]*", TABLE_NAME):
        print(f"Invalid table name: {TABLE_NAME}")
        sys.exit(1)

    if not os.path.exists(DATA_PATH):
        print(f"File not found: {DATA_PATH}")
        sys.exit(1)

    if DATA_PATH.endswith(".parquet"):
        df = pd.read_parquet(DATA_PATH)
    else:
        df = pd.read_csv(DATA_PATH)

    print(f"Loaded {len(df)} rows from {DATA_PATH}")

    if len(df) < REQUIRED_ROWS:
        print(f"Need {REQUIRED_ROWS} rows, got {len(df)}")
        sys.exit(1)

    df = df.head(REQUIRED_ROWS)
    df.columns = [c.lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    df = df.where(pd.notnull(df), None)

    url = URL.create(
        "postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )
    engine = create_engine(url)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connected to DB")

    with engine.begin() as conn:
        df.to_sql(TABLE_NAME, conn, index=False, if_exists="replace")

        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        ).scalar()
        print(f"Inserted {count} rows into {TABLE_NAME}")

        sample = conn.execute(
            text(f"SELECT * FROM {TABLE_NAME} LIMIT 3")
        ).fetchall()
        for row in sample:
            print(f"  {row}")

    print("Done")


if __name__ == "__main__":
    main()