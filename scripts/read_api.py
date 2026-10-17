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
from typing import List, Dict, Set


def fetch_uniprot_data(query: str, size: int = 100) -> List[Dict]:
    """
    Запрашивает данные из UniProt REST API v2.

    Parameters
    ----------
    query : str
        Поисковый запрос в формате UniProt query language.
    size : int, optional
        Максимальное количество записей, по умолчанию 100.

    Returns
    -------
    List[Dict]
        Список словарей с данными о белках.
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"

    # Рабочие поля UniProt API v2 (проверено экспериментально)
    params = {
        "query": query,
        "format": "json",
        "size": size,
        "fields": "accession,id,gene_names,protein_name,organism_name,organism_id,length"
    }

    headers = {
        "User-Agent": "Komarovka-Student/1.0 (educational project)"
    }

    print(f"  Запрос: {query}")

    all_results = []

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(base_url, params=params, headers=headers)

            if response.status_code == 400:
                print(f"    Ошибка 400: Bad Request")
                return []

            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)

            print(f"    Получено {len(results)} записей")

    except httpx.HTTPStatusError as e:
        print(f"    Ошибка HTTP {e.response.status_code}")
    except httpx.HTTPError as e:
        print(f"    Ошибка HTTP: {e}")
    except Exception as e:
        print(f"    Ошибка: {e}")

    return all_results


def parse_uniprot_results(results: List[Dict]) -> pd.DataFrame:
    """
    Преобразует результаты UniProt API в DataFrame.
    """
    parsed_data = []

    for entry in results:
        accession = entry.get("primaryAccession", "N/A")
        protein_id = entry.get("uniProtkbId", "N/A")

        organism_name = entry.get("organism", {}).get("scientificName", "N/A")
        organism_tax_id = entry.get("organism", {}).get("taxonId", "N/A")

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

        protein_info = entry.get("protein", {})
        rec_name = protein_info.get("recommendedName", {})
        protein_full_name = "N/A"

        if rec_name and "fullName" in rec_name:
            fn = rec_name["fullName"]
            if isinstance(fn, dict):
                protein_full_name = fn.get("value", "N/A")
            elif isinstance(fn, list) and fn:
                protein_full_name = fn[0].get("value", "N/A")

        # Функция извлекается из comments (возвращается по умолчанию)
        comments = entry.get("comments", [])
        function_text = "N/A"

        for comment in comments:
            if comment.get("type") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_text = " ".join([t.get("value", "") for t in texts])
                break

        if isinstance(function_text, str) and len(function_text) > 200:
            function_text = function_text[:200] + "..."

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
    Сохраняет DataFrame в CSV и Parquet форматы.
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


def collect_yeast_data(organism_id: int, organism_name: str) -> pd.DataFrame:
    """
    Собирает данные по ферментам ПНЖК для одного вида дрожжей.
    Делает несколько запросов с разными ключевыми словами и объединяет результаты.
    """
    print(f"\n{'=' * 70}")
    print(f"{organism_name}")
    print(f"{'=' * 70}")

    # Несколько простых запросов с разными ключевыми словами
    # UniProt API v2 плохо работает со сложными OR, поэтому делаем отдельно
    queries = [
        f"organism_id:{organism_id} AND desaturase",
        f"organism_id:{organism_id} AND elongase",
        f"organism_id:{organism_id} AND fatty acid",
        f"organism_id:{organism_id} AND lipid",
        f"organism_id:{organism_id} AND PUFA",
    ]

    all_results = []
    seen_accessions: Set[str] = set()

    for query in queries:
        results = fetch_uniprot_data(query, size=100)

        # Удаляем дубликаты по accession
        for entry in results:
            acc = entry.get("primaryAccession", "")
            if acc and acc not in seen_accessions:
                seen_accessions.add(acc)
                all_results.append(entry)

        # Пауза между запросами (этика API)
        time.sleep(1)

    print(f"\n  Всего уникальных записей: {len(all_results)}")

    if all_results:
        df = parse_uniprot_results(all_results)
        df["yeast_type"] = organism_name.split(" (")[0]

        print(f"\n  Первые 5 записей:")
        preview_cols = ["gene_primary", "protein_name", "sequence_length"]
        print(df[preview_cols].head().to_string())

        return df
    else:
        print("  Данные не получены")
        return pd.DataFrame()


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

    # Таксономические ID видов дрожжей
    # 4952 — Yarrowia lipolytica (олеогенные дрожжи)
    # 4932 — Saccharomyces cerevisiae (пекарские дрожжи)
    yeast_species = [
        (4952, "Yarrowia lipolytica (oleogenic yeast)"),
        (4932, "Saccharomyces cerevisiae (baker's yeast)"),
    ]

    all_dataframes = []

    for organism_id, organism_name in yeast_species:
        df = collect_yeast_data(organism_id, organism_name)

        if not df.empty:
            all_dataframes.append(df)

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

        final_df = cast_types(final_df)

        save_dataset(final_df, "scripts/yeast_pufa_enzymes")

        size_kb = final_df.memory_usage(deep=True).sum() / 1024
        print(f"\nРазмер DataFrame в памяти: {size_kb:.2f} KB")

        print()
        print("=" * 70)
        print("ПЕРВЫЕ 20 СТРОК (для скриншота в README):")
        print("=" * 70)
        print(final_df.head(20).to_string())
    else:
        print()
        print("Не удалось получить данные ни по одному виду дрожжей")


if __name__ == "__main__":
    main()