# Dataset: Ферменты биосинтеза ПНЖК у дрожжей

## Источник данных

**UniProt REST API** — универсальная база данных белков и их функций.

- **Официальная документация**: https://www.uniprot.org/help/api
- **Endpoint**: `https://rest.uniprot.org/uniprotkb/search`
- **Формат**: JSON
- **Дата получения**: Октябрь 2026

## Описание

Датасет содержит информацию о **ферментах, участвующих в биосинтезе полиненасыщенных жирных кислот (ПНЖК)** у двух видов дрожжей:

1. **Yarrowia lipolytica** — олеогенные дрожжи, промышленный производитель ПНЖК (омега-3, омега-6)
2. **Saccharomyces cerevisiae** — пекарские дрожжи, модельный организм

### Искомые ферменты

- **Десатуразы** (Δ9, Δ12, Δ15) — вводят двойные связи в жирные кислоты
- **Элонгазы** — удлиняют цепь жирных кислот
- **Ацил-КоА-синтетазы** — активируют жирные кислоты
- Ферменты биосинтеза EPA, DHA, ARA, LA

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

### Примеры запросов

API запросы для получения данных:
- `organism_id:4952 AND (polyunsaturated fatty acid OR desaturase OR elongase OR PUFA OR omega-3 OR omega-6 OR "fatty acid biosynthesis")`
- `organism_id:4932 AND (polyunsaturated fatty acid OR desaturase OR elongase OR PUFA OR "fatty acid biosynthesis")`

## Как использовать

```bash
uv run python scripts/read_api.py