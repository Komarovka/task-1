import argparse

from etl.extract import extract
from etl.load import load
from etl.transform import transform
from etl.validate import validate


def parse_args():
    p = argparse.ArgumentParser(description="ETL: parquet/csv -> homeworks DB")
    p.add_argument("--input", default="data/SC_expression.parquet")
    p.add_argument("--table", default="komarovka")
    p.add_argument("--rows", type=int, default=100)
    return p.parse_args()


def main():
    args = parse_args()

    df = extract(args.input)
    print(f"extracted {len(df)} rows from {args.input}")

    df = transform(df)
    print(f"transformed: {len(df)} rows, {len(df.columns)} cols")

    errors = validate(df)
    if errors:
        for e in errors:
            print("error:", e)
        raise SystemExit(1)

    inserted = load(df.head(args.rows), args.table)
    print(f"loaded {inserted} rows into {args.table}")


if __name__ == "__main__":
    main()