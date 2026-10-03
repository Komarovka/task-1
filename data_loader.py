import pandas as pd
def load_data(file_path: str) -> pd.DataFrame:
    """
    Загружает датасет из CSV файла.
    Args:
        file_path (str): Путь к файлу с данными
    Returns:
        pd.DataFrame: Загруженный датасет
    """
    return pd.read_csv(file_path)
if __name__ == '__main__':
    dataset_path = 'SC_expression.csv'
    df = load_data(dataset_path)
    print(f"Загружено строк: {len(df)}, колонок: {len(df.columns)}")
    print("\nПервые 10 строк датасета:")
    print(df.head(10))
