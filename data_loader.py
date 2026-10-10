import pandas as pd
import requests
import tempfile
import os


def get_yandex_disk_download_url(public_key: str) -> str:
    """
    Получение ссылки на скачивание Яндекс.Диска.
    """
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    response = requests.get(api_url, params={"public_key": public_key}, timeout=30)
    response.raise_for_status()
    return response.json()["href"]


def load_data(url: str) -> pd.DataFrame:
    """
    Загрузка датасета по ссылке.

    Args:
        url (str): Публичная ссылка на датасет.

    Returns:
        pd.DataFrame: Загруженный датасет.
    """
    if "disk.yandex.ru" in url or "yadi.sk" in url:
        download_url = get_yandex_disk_download_url(url)
    else:
        download_url = url

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        response = requests.get(download_url, timeout=(10, 300))
        response.raise_for_status()
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    try:
        df = pd.read_csv(tmp_path)
        return df
    finally:
        os.unlink(tmp_path)


if __name__ == '__main__':
    dataset_url = 'https://disk.yandex.ru/d/4bQoE0M7EvDYxg'

    print("Загрузка данных из Яндекс.Диск...")
    df = load_data(dataset_url)

    print(f"Успешно загружено строк: {len(df)}, колонок: {len(df.columns)}")
    print("\nПервые 10 строк датасета:")
    print(df.head(10))
