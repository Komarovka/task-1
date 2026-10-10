"""
Скрипт для загрузки, приведения типов и сохранения датасета
SC_expression (транскриптомика дрожжей) в формат Parquet.

Домашнее задание №3 по курсу "ИИ инжиниринг".
"""

import pandas as pd


def read_csv(path: str) -> pd.DataFrame:
    """Читает CSV-файл и возвращает DataFrame."""
    df = pd.read_csv(path)
    print(f"Загружено {df.shape[0]} строк и {df.shape[1]} колонок из {path}")
    return df


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводит типы данных DataFrame к оптимальным для экономии памяти.

    Правила приведения:
    - float64 -> float32 (числовые значения экспрессии генов)
    - object с небольшим числом уникальных значений -> category
    - Бинарные числовые колонки (0/1) -> Int8 (nullable)
    """
    df = df.copy()

    for col in df.columns:
        dtype = df[col].dtype

        # Приводим float64 к float32 — экономия памяти в 2 раза
        if dtype == "float64":
            df[col] = df[col].astype("float32")

        # Приводим int64 к int32, если значения помещаются
        elif dtype == "int64":
            min_val = df[col].min()
            max_val = df[col].max()
            if min_val >= -32768 and max_val <= 32767:
                df[col] = df[col].astype("int16")
            elif min_val >= -2147483648 and max_val <= 2147483647:
                df[col] = df[col].astype("int32")

        # Строковые колонки с малым числом уникальных значений -> category
        elif dtype == "object":
            nunique = df[col].nunique()
            if nunique < len(df) * 0.5:  # меньше 50% уникальных
                df[col] = df[col].astype("category")

    print("Приведение типов завершено.")
    print("Новые типы данных:")
    print(df.dtypes.value_counts().to_string())
    return df


def save_parquet(df: pd.DataFrame, path: str) -> None:
    """Сохраняет DataFrame в формат Parquet."""
    df.to_parquet(path, engine="pyarrow", index=False)
    print(f"DataFrame сохранён в {path}")


if __name__ == "__main__":
    INPUT_PATH = "data/SC_expression.csv"
    OUTPUT_PATH = "data/SC_expression.parquet"

    df = read_csv(INPUT_PATH)
    df = cast_types(df)
    save_parquet(df, OUTPUT_PATH)

    print("\n=== Информация о сохранённом файле ===")
    print(f"Размер исходного DataFrame: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")