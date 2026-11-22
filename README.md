# ИСППР по обслуживанию оборудования — LLM-агент + RAG

[![CI](https://github.com/Xalegor1/equipment-maintenance-rag-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Xalegor1/equipment-maintenance-rag-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Tests](https://img.shields.io/badge/tests-60%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Учебно-исследовательская система поддержки принятия решений по техническому
обслуживанию (ТО) промышленного оборудования. Агент отвечает на вопросы
обслуживающего персонала: что обслуживать, когда, с какими работами и какие
регламенты при этом действуют.

Отличие от «обычного чата по PDF»: агент не только ищет по документации, но и
**вызывает инструмент с базой оборудования** — получает конкретную единицу, её
даты ТО и параметры, считает просрочку и отвечает с дословной атрибуцией
источника.

## Возможности

- **LLM-агент** на LangChain ReAct с двумя инструментами: `search_documentation`
  (RAG по регламентам) и `query_equipment_db` (данные о единице оборудования).
- **Гибридный поиск**: dense-эмбеддинги (pgvector, HNSW) + полнотекстовый поиск
  PostgreSQL (русская конфигурация), результаты объединяются.
- **Дословная атрибуция**: цитата из документа с указанием файла и страницы.
- **Честность по теме**: если в базе знаний нет ответа, агент это говорит.
- **Загрузка документов** через UI и `POST /api/v1/ingest`, список — `GET /documents`.
- **Оценка качества** по RAGAS: faithfulness, answer relevancy, context recall,
  context precision; прогоны конфигурируются по `chunk_size` (256/512/1024).
- **60 тестов**, ruff и mypy в CI-режиме; Docker Compose поднимает весь стек.

## Архитектура

```
Streamlit (UI)  →  FastAPI
                     └─ LLM-агент (LangChain ReAct, gpt-4o-mini)
                          ├─ tool: search_documentation → RAG по pgvector
                          └─ tool: query_equipment_db   → таблица equipment
                     RAG-конвейер: loader → chunker → embedder → retriever → generator
                                       ↓
                          PostgreSQL + pgvector (документы + оборудование)
```

Подробнее — в [docs/architecture.md](docs/architecture.md) и в курсовой работе
[docs/Курсовая_работа_RAG_Еловенко.docx](docs/Курсовая_работа_RAG_Еловенко.docx).

## Стек

| Слой | Технологии |
|---|---|
| LLM | gpt-4o-mini через LangChain |
| Агент | LangChain ReAct (AgentExecutor), tool-calling |
| Эмбеддинги | `text-embedding-3-small` (1536) |
| Векторное хранилище | PostgreSQL + pgvector (HNSW, косинус) |
| База оборудования | PostgreSQL, таблица `equipment` |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Оценка | RAGAS |
| Инфраструктура | Docker Compose (postgres + api + frontend), Makefile |

## Быстрый старт (Docker)

```bash
cp .env.example .env
# укажите OPENAI_API_KEY и смените POSTGRES_PASSWORD

docker compose up --build
# API:      http://localhost:8000/docs
# Frontend: http://localhost:8501
```

При первом запуске Postgres сам создаёт схему и наполняет таблицу оборудования
демо-записями (`docker/init.sql`). Полный сброс:
`docker compose down -v && docker compose up --build`.

Загрузка документов — через сайдбар UI или `POST /api/v1/ingest`.

## Запуск без Docker

Нужен PostgreSQL с расширением pgvector:

```bash
docker compose up -d postgres

python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env              # OPENAI_API_KEY + POSTGRES_DSN (host=localhost)

make dev        # API
make frontend   # Streamlit
```

## API

```bash
# карточка оборудования (seed)
curl http://localhost:8000/api/v1/equipment/ПК-630/10-2

# вопрос агенту
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"question":"Трансформатор ПК-630/10-2 давно не обслуживался — что делать?"}'

# вопрос только к RAG, без агента
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Каков порядок подготовки трансформатора?"}'
```

## Структура

```
src/
├── agent/        # инструменты, промпт, AgentExecutor, сервис, исключения
├── db/           # PostgreSQL: пул соединений (+pgvector), репозиторий оборудования
├── rag/          # loader, chunker, embedder, vector_store, retriever, generator, pipeline
├── api/          # FastAPI: роуты, схемы, зависимости
└── eval/         # RAGAS-оценка и генератор тестсета
frontend/         # Streamlit
docker/init.sql   # схема БД и seed оборудования
configs/          # YAML-конфиги экспериментов по chunk_size
tests/            # unit + integration (60 тестов)
docs/             # курсовая, шпаргалки, архитектура
```

## Данные

В `data/docs/` лежат два регламента, на которых собран демо-корпус:
РД 34.45-51.300-97 и «Правила технической эксплуатации электроустановок
потребителей». Корпус расширяется любыми PDF через API или UI; для доменной
оценки пересоберите тестсет по своим документам (см. ниже).

## Тесты и линт

```bash
make test       # 60 тестов
make lint       # ruff + mypy
```

## Оценка качества (RAGAS)

```bash
# сначала загрузите корпус, затем прогон
python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml --ingest-docs data/docs/
```

Конфиги `v1/v2/v3` отличаются размером чанка. Метрики: faithfulness,
answer_relevancy, context_recall, context_precision.

> **Оговорка про тестсет.** `data/eval/testset.json` собран на трёх статьях по
> машинному обучению (`data/eval/sample_docs/`), а не на ГОСТах — это унаследованный
> датасет от первой версии. Для доменной оценки пересоберите его:
> `make generate-testset` по документам из `data/docs/`.

## Ограничения

- Оценка и генерация требуют ключа OpenAI; локальные модели не поддерживаются.
- Гибридный поиск и HNSW настроены под русскоязычные регламенты, для других
  языков нужна правка конфигурации PostgreSQL.
- Промпт-гардрейлы эвристические, не заменяют модель-классификатор.
- Демо-база оборудования — синтетическая, не для промышленной эксплуатации.

## Лицензия

MIT — см. [LICENSE](LICENSE).

Автор: Егор Еловенко · [GitHub](https://github.com/Xalegor1)
