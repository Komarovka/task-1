import re

import pandas as pd


def validate(df: pd.DataFrame, min_rows: int = 1) -> list[str]:
    errors = []
    if df.empty:
        errors.append("empty dataframe")
    if len(df) < min_rows:
        errors.append(f"too few rows: {len(df)} < {min_rows}")
    if any(df.columns.duplicated()):
        errors.append("duplicate column names")
    if any(not re.fullmatch(r"[a-z_][a-z0-9_]*", c) for c in df.columns):
        errors.append("column names must be snake_case")
    return errors