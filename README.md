# Домашнее задание 2: анализ транскриптомики дрожжей

## Домашнее задание 1
Ссылка на Яндекс.Диск с файлом csv из kaggle: https://disk.yandex.ru/d/4bQoE0M7EvDYxg
Описание проекта: тематика данных связана с моей научной деятельностью: индуцированный мутагенез олеогенных дрожжей
Ссылка на kaggle: https://www.kaggle.com/datasets/costalaether/yeast-transcriptomics
Описание данных: 6071 unique values; 93 columns

## Домашнее задание 2
Тематика: индуцированный мутагенез олеогенных дрожжей.
Источник: https://disk.yandex.ru/d/4bQoE0M7EvDYxg
Датасет содержит 6071 строк и 93 колонки.

## Установка окружения
1. Клонирование репозитория:
   ```bash
   git clone https://github.com/Komarovka/task-1.git
   cd task-1

   ## Пакет etl

Этап ETL собран в пакет `src/etl`:

| Модуль | Назначение |
|---|---|
| extract.py | чтение parquet/csv |
| transform.py | snake_case колонок, дедупликация, очистка |
| validate.py | проверки перед записью |
| load.py | запись в PostgreSQL (homeworks) |
| main.py | CLI-точка входа |

### Запуск

```bash
$env:PYTHONPATH = "src"
uv run python -m etl.main --input data/SC_expression.parquet --table komarovka --rows 100