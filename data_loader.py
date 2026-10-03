import pandas as pd
import os

def load_and_display_data(file_path: str, n_rows: int = 10):
    """
    Загружает датасет и выводит первые n строк.
    """
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return None
    
    df = pd.read_csv(file_path)
    print(f"✅ Загружено строк: {len(df)}, колонок: {len(df.columns)}")
    print(f"\nПервые {n_rows} строк датасета:")
    print(df.head(n_rows))
    return df

if __name__ == '__main__':
    dataset_path = 'SC_expression.csv'
    load_and_display_data(dataset_path)
