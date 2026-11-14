import re

import pandas as pd


def _clean_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name or name[0].isdigit():
        name = "col_" + name
    return name


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_clean_name(c) for c in df.columns]
    if "unnamed_0" in df.columns:
        df = df.drop(columns=["unnamed_0"])
    df = df.drop_duplicates()
    df = df.dropna(how="all")
    return df.reset_index(drop=True)