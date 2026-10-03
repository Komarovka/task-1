import pandas as pd
import os

def load_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл '{file_path}' не найден.")
    return pd.read_csv(file_path)
    
if __name__ == '__main__':
    dataset_path = 'SC_expression.csv'
    
    df = load_data(dataset_path)   
    print(f"✅ Загружено строк: {len(df)}, колонок: {len(df.columns)}")
    print(f"\nПервые 10 строк датасета:")
    print(df.head(10))
