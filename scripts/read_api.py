"""
Скрипт для получения данных о ферментах биосинтеза ПНЖК у дрожжей
через UniProt REST API.

Собирает информацию о белках, участвующих в синтезе полиненасыщенных
жирных кислот (ПНЖК): десатуразы, элонгазы, ацил-КоА-синтетазы и др.

Виды дрожжей:
- Yarrowia lipolytica (олеогенные дрожжи, промышленный производитель ПНЖК)
- Saccharomyces cerevisiae (модельный организм)

Источники:
- UniProt REST API v2: https://rest.uniprot.org/
- Документация: https://www.uniprot.org/help/api

Автор: Komarovka
Дата: Октябрь 2026
Домашнее задание №4 (вариант 1: Public API)
"""

import httpx
import pandas as pd
import time
from typing import List, Dict


def fetch_uniprot_data(query: str, size: int = 100) -> List[Dict]:
    """
    Запрашивает данные из UniProt REST API v2.

    Parameters
    ----------
    query : str
        Поисковый запрос в формате UniProt query language.
        Используются organism_id и ключевые слова по ПНЖК.
    size : int, optional
        Максимальное количество записей, по умолчанию 100.

    Returns
    -------
    List[Dict]
        Список словарей с данными о белках.
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"

    # Поля, которые точно поддерживаются UniProt API v2
    params = {
        "query": query,
        "format": "json",
        "size": size,
        "fields": "accession,id,gene_names,protein_name,organism_name,organism_id,length,comment_function"
    }

    headers = {
        "User-Agent": "Komarovka-Student/1.0 (educational project)"
    }

    print(f"Запрос к UniProt API: {query}")
    print(f"  Ожидаемое количество записей: до {size}")

    all_results = []

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(base_url, params=params, headers=headers)

            if response.status_code == 400:
                print(f"Ошибка 400: Bad Request")
                print(f"  URL: {response.url}")
                print(f"  Ответ: {response.text[:300]}")
                return []

            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)

            print(f"Получено {len(results)} записей")

    except httpx.HTTPStatusError as e:
        print(f"Ошибка HTTP {e.response.status_code}: {e.response.reason_phrase}")
        print(f"  URL: {e.request.url}")
    except httpx.HTTPError as e:
        print(f"Ошибка HTTP: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

    return all_results


def parse_uniprot_results(results: List[Dict]) -> pd.DataFrame:
    """
    Преобразует результаты UniProt API в DataFrame.

    Parameters
    ----------
    results : List[Dict]
        Список словарей с данными от UniProt.

    Returns
    -------
    pd.DataFrame
        Датафрейм с извлечёнными данными.
    """
    parsed_data = []

    for entry in results:
        # Основные идентификаторы
        accession = entry.get("primaryAccession", "N/A")
        protein_id = entry.get("uniProtkbId", "N/A")

        # Организм
        organism_name = entry.get("organism", {}).get("scientificName", "N/A")
        organism_tax_id = entry.get("organism", {}).get("taxonId", "N/A")

        # Гены
        genes = entry.get("genes", [])
        gene_names_list = []

        if genes:
            for gene in genes:
                if "primaryName" in gene:
                    gene_names_list.append(gene["primaryName"].get("value", ""))
                if "synonyms" in gene:
                    gene_names_list.extend(
                        [syn.get("value", "") for syn in gene["synonyms"]]
                    )

        gene_primary = gene_names_list[0] if gene_names_list else "N/A"
        gene_synonyms = (
            ";".join(gene_names_list[1:]) if len(gene_names_list) > 1 else "N/A"
        )

        # Название белка
        protein_info = entry.get("protein", {})
        rec_name = protein_info.get("recommendedName", {})
        protein_full_name = "N/A"

        if rec_name and "fullName" in rec_name:
            fn = rec_name["fullName"]
            if isinstance(fn, dict):
                protein_full_name = fn.get("value", "N/A")
            elif isinstance(fn, list) and fn:
                protein_full_name = fn[0].get("value", "N/A")

        # Функция (комментарий FUNCTION)
        comments = entry.get("comments", [])
        function_text = "N/A"

        for comment in comments:
            if comment.get("type") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_text = " ".join([t.get("value", "") for t in texts])
                break

        # Ограничим длину функции, чтобы таблица читалась
        if len(function_text) > 200:
            function_text = function_text[:200] + "..."

        # Длина последовательности
        sequence = entry.get("sequence", {})
        length = sequence.get("length", "N/A")

        parsed_data.append(
            {
                "accession": accession,
                "protein_id": protein_id,
                "gene_primary": gene_primary,
                "gene_synonyms": gene_synonyms,
                "protein_name": protein_full_name,
                "organism": organism_name,
                "taxon_id": organism_tax_id,
                "function": function_text,
                "sequence_length": length,
            }
        )

    return pd.DataFrame(parsed_data)


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводит типы данных DataFrame для оптимизации памяти.

    - sequence_length: Int16 (nullable integer)
    - taxon_id: Int32 (nullable integer)
    """
    df = df.copy()

    if "sequence_length" in df.columns:
        df["sequence_length"] = pd.to_numeric(
            df["sequence_length"], errors="coerce"
        ).astype("Int16")

    if "taxon_id" in df.columns:
        df["taxon_id"] = pd.to_numeric(
            df["taxon_id"], errors="coerce"
        ).astype("Int32")

    print("Приведение типов завершено")
    print(df.dtypes)

    return df


def save_dataset(df: pd.DataFrame, output_path: str) -> None:
    """
    Сохраняет DataFrame в CSV формат.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame для сохранения.
    output_path : str
        Путь к выходному файлу (без расширения).
    """
    csv_path = output_path + ".csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Данные сохранены в {csv_path}")

    try:
        parquet_path = output_path + ".parquet"
        df.to_parquet(parquet_path, index=False, engine="pyarrow")
        print(f"Данные сохранены в {parquet_path}")
    except ImportError:
        print("pyarrow не установлен, Parquet пропущен")
    except Exception as e:
        print(f"Ошибка при сохранении Parquet: {e}")


def main():
    """
    Основная функция: запрашивает данные по ферментам биосинтеза ПНЖК
    у двух видов дрожжей и сохраняет результат в CSV.
    """
    print("=" * 70)
    print("UniProt API: Ферменты биосинтеза ПНЖК у дрожжей")
    print("=" * 70)
    print()
    print("Полиненасыщенные жирные кислоты (ПНЖК):")
    print("  - Омега-3: EPA (эйкозапентаеновая), DHA (докозагексаеновая)")
    print("  - Омега-6: LA (линолевая), ARA (арахидоновая)")
    print()
    print("Искомые ферменты: десатуразы, элонгазы, ацил-КоА-синтетазы")
    print("=" * 70)

    # Используем таксономические ID и ключевые слова по ПНЖК
    # 4952 — Yarrowia lipolytica (олеогенные дрожжи, промышленный производитель ПНЖК)
    # 4932 — Saccharomyces cerevisiae (пекарские дрожжи, модельный организм)
    queries = {
        "Yarrowia lipolytica (oleogenic yeast)":
            'organism_id:4952 AND (polyunsaturated fatty acid OR desaturase OR elongase OR PUFA OR omega-3 OR omega-6 OR "fatty acid biosynthesis")',
        "Saccharomyces cerevisiae (baker's yeast)":
            'organism_id:4932 AND (polyunsaturated fatty acid OR desaturase OR elongase OR PUFA OR "fatty acid biosynthesis")',
    }

    all_dataframes = []

    for description, query in queries.items():
        print()
        print("=" * 70)
        print(description)
        print("=" * 70)

        results = fetch_uniprot_data(query, size=100)

        if results:
            df = parse_uniprot_results(results)
            df["yeast_type"] = description.split(" (")[0]

            print()
            print("Первые 5 записей:")
            preview_cols = ["gene_primary", "protein_name", "sequence_length"]
            print(df[preview_cols].head().to_string())

            all_dataframes.append(df)

            # Пауза между запросами — этичное использование API
            print()
            print("Пауза 2 секунды перед следующим запросом...")
            time.sleep(2)
        else:
            print("Данные не получены, переходим к следующему виду")

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)

        print()
        print("=" * 70)
        print("ИТОГО:")
        print("=" * 70)
        total = len(final_df)
        unique_genes = final_df["gene_primary"].nunique()
        unique_types = final_df["yeast_type"].nunique()
        print(f"Всего записей: {total}")
        print(f"Уникальных генов: {unique_genes}")
        print(f"Видов дрожжей: {unique_types}")

        # Приведение типов
        final_df = cast_types(final_df)

        # Сохранение