"""
Скрипт для получения данных о ферментах биосинтеза ПНЖК у дрожжей
через UniProt REST API.

Собирает информацию о белках, участвующих в синтезе полиненасыщенных
жирных кислот (ПНЖК): десатуразы, элонгазы и др.

Виды дрожжей:
- Yarrowia lipolytica (олеогенные дрожжи, промышленный производитель ПНЖК)
- Saccharomyces cerevisiae (модельный организм)

Источники:
- UniProt REST API v2: https://rest.uniprot.org/
- Документация: https://www.uniprot.org/help/api

Автор: Komarovka
Дата: 2026-10-23
Домашнее задание №4 (вариант 1: Public API)
"""

import sys
import httpx
import pandas as pd
import time
from typing import List, Dict, Tuple

# ============================================================================
# КОНСТАНТЫ
# ============================================================================

BASE_URL = "https://rest.uniprot.org/uniprotkb/search"

# Поля, которые точно поддерживаются UniProt API v2
REQUEST_FIELDS = "accession,id,gene_names,protein_name,organism_name,organism_id,length"

# GO-термины (проверены на QuickGO):
# GO:0006633 — fatty acid biosynthetic process
# GO:0006631 — fatty acid metabolic process
# GO:0004768 — acyl-CoA desaturase activity
# Ключевые слова: desaturase, elongase
YEAST_QUERIES: List[Tuple[int, str, str]] = [
    (4952, "Yarrowia lipolytica (oleogenic yeast)",
     "organism_id:4952 AND (go:0006633 OR go:0006631 OR go:0004768 OR desaturase OR elongase)"),
    (4932, "Saccharomyces cerevisiae (baker's yeast)",
     "organism_id:4932 AND (go:0006633 OR go:0006631 OR go:0004768 OR desaturase OR elongase)"),
]

HEADERS = {
    "User-Agent": "Komarovka-Student/1.0 (educational project, ITMO 2026)"
}


def fetch_uniprot_data(query: str, size: int = 100) -> List[Dict]:
    """
    Запрашивает данные из UniProt REST API v2 с пагинацией.

    Parameters
    ----------
    query : str
        Поисковый запрос в формате UniProt query language.
    size : int, optional
        Размер страницы, по умолчанию 100.

    Returns
    -------
    List[Dict]
        Список словарей с данными о белках.

    Raises
    ------
    RuntimeError
        Если API вернул ошибку или не удалось получить данные.
    """
    params = {
        "query": query,
        "format": "json",
        "size": size,
        "fields": REQUEST_FIELDS,
    }

    all_results: List[Dict] = []
    url = BASE_URL

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            while url:
                response = client.get(url, params=params if url == BASE_URL else None,
                                      headers=HEADERS)
                response.raise_for_status()

                total_header = response.headers.get("x-total-results", "?")
                print(f"    x-total-results: {total_header}")

                data = response.json()
                results = data.get("results", [])
                all_results.extend(results)

                next_url = response.links.get("next", {}).get("url")
                if next_url:
                    url = next_url
                    params = None
                    print(f"    Загружена страница, всего записей: {len(all_results)}")
                else:
                    url = None

    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Ошибка HTTP {e.response.status_code} при запросе: {query}\n"
            f"URL: {e.request.url}\n"
            f"Ответ: {e.response.text[:300]}"
        ) from e
    except httpx.HTTPError as e:
        raise RuntimeError(f"Ошибка HTTP при запросе: {query}\n{e}") from e

    return all_results


def extract_gene_info(entry: Dict) -> Tuple[str, str]:
    """
    Извлекает основное название гена и синонимы из записи UniProt.

    Returns
    -------
    Tuple[str, str]
        (gene_primary, gene_synonyms)
    """
    genes = entry.get("genes", [])
    if not genes:
        return "N/A", "N/A"

    gene = genes[0]

    primary = "N/A"
    if "geneName" in gene:
        primary = gene["geneName"].get("value", "N/A")
    elif "primaryName" in gene:
        primary = gene["primaryName"].get("value", "N/A")

    synonyms = []
    if "synonyms" in gene:
        synonyms = [syn.get("value", "") for syn in gene["synonyms"]]

    gene_synonyms = ";".join(synonyms) if synonyms else "N/A"

    return primary, gene_synonyms


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

        gene_primary, gene_synonyms = extract_gene_info(entry)

        protein_info = entry.get("protein", {})
        rec_name = protein_info.get("recommendedName", {})
        protein_full_name = "N/A"

        if rec_name and "fullName" in rec_name:
            fn = rec_name["fullName"]
            if isinstance(fn, dict):
                protein_full_name = fn.get("value", "N/A")
            elif isinstance(fn, list) and fn:
                protein_full_name = fn[0].get("value", "N/A")

        comments = entry.get("comments", [])
        function_text = "N/A"

        for comment in comments:
            if comment.get("type") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_text = " ".join([t.get("value", "") for t in texts])
                break

        sequence = entry.get("sequence", {})
        length = sequence.get("length", "N/A")

        parsed_data.append({
            "accession": accession,
            "protein_id": protein_id,
            "gene_primary": gene_primary,
            "gene_synonyms": gene_synonyms,
            "protein_name": protein_full_name,
            "organism": organism_name,
            "taxon_id": organism_tax_id,
            "function": function_text,
            "sequence_length": length,
        })

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


def collect_yeast_data(organism_id: int, organism_name: str, query: str) -> pd.DataFrame:
    """
    Собирает данные по ферментам ПНЖК для одного вида дрожжей.
    """
    print(f"\n{'=' * 70}")
    print(f"{organism_name}")
    print(f"{'=' * 70}")
    print(f"  Запрос: {query}")

    results = fetch_uniprot_data(query, size=100)

    if not results:
        print("  По запросу не получено ни одной записи")
        return pd.DataFrame()

    seen_accessions: set = set()
    unique_results = []
    for entry in results:
        acc = entry.get("primaryAccession", "")
        if acc and acc not in seen_accessions:
            seen_accessions.add(acc)
            unique_results.append(entry)

    print(f"  Получено {len(results)} записей, уникальных: {len(unique_results)}")

    df = parse_uniprot_results(unique_results)
    df["yeast_type"] = organism_name.split(" (")[0]

    print(f"\n  Первые 5 записей:")
    preview_cols = ["gene_primary", "protein_name", "sequence_length"]
    print(df[preview_cols].head().to_string())

    return df


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
    print("Используемые запросы:")
    print("  - GO:0006633 (fatty acid biosynthetic process)")
    print("  - GO:0006631 (fatty acid metabolic process)")
    print("  - GO:0004768 (acyl-CoA desaturase activity)")
    print("  - desaturase, elongase (ключевые слова)")
    print("=" * 70)

    all_dataframes = []

    for organism_id, organism_name, query in YEAST_QUERIES:
        try:
            df = collect_yeast_data(organism_id, organism_name, query)
            if not df.empty:
                all_dataframes.append(df)
            else:
                print(f"  ⚠️  Пропускаем {organism_name}: нет данных по запросу")
        except RuntimeError as e:
            print(f"\n Ошибка при обработке {organism_name}:")
            print(f"   {e}")
            print(f"  ⚠️  Пропускаем {organism_name} из-за ошибки API")

        time.sleep(1)

    if not all_dataframes:
        print("\n❌ Не удалось получить данные ни по одному виду дрожжей")
        print("Проверьте запросы или подключение к интернету")
        sys.exit(1)

    final_df = pd.concat(all_dataframes, ignore_index=True)

    print()
    print("=" * 70)
    print("ИТОГО:")
    print("=" * 70)

    final_df = cast_types(final_df)

    total = len(final_df)
    unique_genes = final_df["gene_primary"].nunique()
    unique_types = final_df["yeast_type"].nunique()
    print(f"Всего записей: {total}")
    print(f"Уникальных генов: {unique_genes}")
    print(f"Видов дрожжей: {unique_types}")

    save_dataset(final_df, "scripts/yeast_pufa_enzymes")

    size_kb = final_df.memory_usage(deep=True).sum() / 1024
    print(f"\nРазмер DataFrame в памяти: {size_kb:.2f} KB")

    print()
    print("=" * 70)
    print("ПЕРВЫЕ 20 СТРОК (для скриншота в README):")
    print("=" * 70)
    print(final_df.head(20).to_string())


if __name__ == "__main__":
    main()