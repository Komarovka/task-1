# Dataset: Ферменты биосинтеза ПНЖК у дрожжей

## Источник данных

**UniProt REST API v2** — универсальная база данных белков и их функций.

- **Официальная документация**: https://www.uniprot.org/help/api
- **Endpoint**: `https://rest.uniprot.org/uniprotkb/search`
- **Формат**: JSON
- **Дата получения**: 2026-10-17

## Описание

Датасет содержит информацию о **ферментах, участвующих в биосинтезе полиненасыщенных жирных кислот (ПНЖК)** у двух видов дрожжей:

1. **Yarrowia lipolytica** — олеогенные дрожжи, промышленный производитель ПНЖК (омега-3, омега-6)
2. **Saccharomyces cerevisiae** — пекарские дрожжи, модельный организм

### Искомые ферменты

Запросы сужены до конкретных ферментов ПНЖК-пути (не просто "lipid"):
- **Десатуразы** (fatty acid desaturase) — вводят двойные связи в жирные кислоты
- **Элонгазы** (fatty acid elongase) — удлиняют цепь жирных кислот

### Поля датасета

| Поле | Описание | Тип в коде |
|------|----------|-----------|
| `accession` | Уникальный идентификатор UniProt | str |
| `protein_id` | ID белка в формате UniProtKB | str |
| `gene_primary` | Основное название гена (из geneName) | str |
| `gene_synonyms` | Синонимы гена (через `;`) | str |
| `protein_name` | Рекомендованное название белка | str |
| `organism` | Научное название организма | str |
| `taxon_id` | Таксономический ID (NCBI) | Int32 (nullable) |
| `function` | Описание функции белка (полный текст из comments) | str |
| `sequence_length` | Длина аминокислотной последовательности | Int16 (nullable) |
| `yeast_type` | Вид дрожжей | str |

### Примеры запросов

API запросы для получения данных:
- `organism_id:4952 AND (desaturase OR elongase OR "fatty acid desaturase" OR "fatty acid elongase")`
- `organism_id:4932 AND (desaturase OR elongase OR "fatty acid desaturase" OR "fatty acid elongase")`

## Как использовать

```bash
uv run python scripts/read_api.py

## 📊 Визуализация данных (ДЗ №6)

Для визуализации использована библиотека **Plotly** с настройками для отображения в GitHub.

### Настройка рендеринга

```python
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "png"
pio.templates.default = "plotly_white"

### Комплексная визуализация (сетка 2x2)

![Анализ ферментов ПНЖК](data/pufa_enzymes_grid.png)

**Описание графиков:**
1. **Гистограмма** — распределение длины белковых последовательностей по видам
2. **Bar chart** — количество ферментов по видам дрожжей (5 у Y. lipolytica, 2 у S. cerevisiae)
3. **Bar chart** — длина последовательностей по конкретным генам (MFE2, PAH1, FAS2, BIO1)
4. **Scatter plot** — связь таксономического ID и длины белка

### Дополнительные визуализации

#### Box plot — статистическое распределение
![Box plot](data/boxplot_length.png)

#### Pie chart — распределение по видам
![Pie chart](data/pie_distribution.png)

#### Scatter — многомерный анализ
![Scatter](data/scatter_multidim.png)

### Единый стиль

Все графики используют:
- Кастомную цветовую палитру (красный для Y. lipolytica, бирюзовый для S. cerevisiae)
- Шрифт Arial, размер 12-16
- Шаблон `plotly_white`
- Интерактивные hover-подсказки