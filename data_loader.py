import pandas as pd
import requests
import tempfile
import os

def get_yandex_disk_download_url(public_key: str) -> str:
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    response = requests.get(api_url, params={"public_key": public_key})
    response.raise_for_status()
    return response.json()["href"]

def load_data(url: str) -> pd.DataFrame:
    if "disk.yandex.ru" in url or "yadi.sk" in url:
        download_url = get_yandex_disk_download_url(url)
    else:
        download_url = url
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        response = requests.get(download_url)
        response.raise_for_status()
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    try:
        # Читаем CSV через pandas
        df = pd.read_csv(tmp_path)
        return df
    finally:
        # Удаляем временный файл после чтения
        os.unlink(tmp_path)


if __name__ == '__main__':
    # Ссылка на Яндекс.Диск с датасетом
    dataset_url = 'https://disk.yandex.ru/d/4bQoE0M7EvDYxg'
    
    print("Загрузка данных...")
    df = load_data(dataset_url)
    
    print(f"Успешно загружено строк: {len(df)}, колонок: {len(df.columns)}")
    print("\nПервые 10 строк датасета:")
    print(df.head(10))
