# Dataset: Белки дрожжей, участвующие в метаболизме липидов

## Источник данных

**UniProt REST API** — универсальная база данных белков и их функций.

- **Официальная документация**: https://www.uniprot.org/help/api
- **Endpoint**: `https://rest.uniprot.org/uniprotkb/search`
- **Формат**: JSON
- **Дата получения**: Октябрь 2026

## Описание

Датасет содержит информацию о белках двух видов дрожжей, участвующих в метаболизме липидов:

1. **Yarrowia lipolytica** — олеогенные дрожжи (накапливают липиды)
2. **Saccharomyces cerevisiae** — пекарские дрожжи (модельный организм)

### Поля датасета

| Поле | Описание | Тип |
|------|----------|-----|
| `accession` | Уникальный идентификатор UniProt | str |
| `protein_id` | ID белка в формате UniProtKB | str |
| `gene_primary` | Основное название гена | str |
| `gene_synonyms` | Синонимы гена (через `;`) | str |
| `protein_name` | Рекомендованное название белка | str |
| `organism` | Научное название организма | str |
| `taxon_id` | Таксономический ID (NCBI) | int |
| `function` | Описание функции белка | str |
| `sequence_length` | Длина аминокислотной последовательности | int |
| `yeast_type` | Вид дрожжей | category |

## Как использовать

```bash
uv run python scripts/read_api.py