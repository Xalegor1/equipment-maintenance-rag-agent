# ИСППР по техническому обслуживанию оборудования (LLM-агент + RAG)

Интеллектуальная информационная система поддержки принятия решений при техническом
обслуживании высоковольтного электрооборудования. Система отвечает на вопросы инженеров-
энергетиков, **комбинируя данные о конкретном оборудовании из БД с требованиями нормативной
документации** (ГОСТы, РД, ПТЭЭП) и формируя обоснованную рекомендацию.

Курсовая работа, 4 семестр (УУНиТ). Прототип построен на основе RAG-системы DocMind с
добавлением агентного слоя и заменой облачного векторного хранилища на локальный PostgreSQL/pgvector.

## Чем отличается от обычного RAG

| | Чистый RAG | LLM-агент (этот проект) |
|---|---|---|
| Шаги | Фиксированные: вопрос → поиск → ответ | Агент сам планирует шаги |
| Источники | Только документация | Документация **+ база оборудования** |
| Пример | «Какова периодичность осмотра трансформатора?» | «Трансформатор ТМ-630/10-2 давно не осматривался — что делать?» |

Агент на запрос с идентификатором оборудования сначала запрашивает БД (дата последнего
осмотра, статус), затем ищет норматив в документации, и комбинирует это в рекомендацию со
ссылкой на ГОСТ. Оба режима доступны в интерфейсе — для наглядного сравнения.

## Архитектура

```
Streamlit (UI)  →  FastAPI  →  ┌─ LLM-агент (LangChain ReAct, gpt-4o-mini)
                               │     ├─ tool: search_documentation  → RAG по pgvector
                               │     └─ tool: query_equipment_db     → таблица equipment
                               └─ RAG-конвейер (loader → chunker → embedder → retriever → generator)
                                          ↓
                               PostgreSQL + pgvector (документация + оборудование)
```

- **LLM-агент**: `langchain.agents.create_react_agent` + `AgentExecutor`. Паттерн ReAct
  (Reasoning + Acting) — агент чередует размышления, вызовы инструментов и наблюдения.
  Полный трейс шагов возвращается в API и отображается в UI.
- **RAG**: PDF → очистка текста ГОСТов → чанкинг (RecursiveCharacterTextSplitter с учётом
  нумерации пунктов) → эмбеддинги OpenAI text-embedding-3-small (1536) → поиск по косинусу (HNSW).
- **Два инструмента агента**: `search_documentation(query)` и `query_equipment_db(equipment_id)`.

## Стек

| Слой | Технология |
|---|---|
| LLM | gpt-4o-mini (LangChain) |
| Агент | LangChain ReAct (AgentExecutor) |
| Эмбеддинги | OpenAI text-embedding-3-small (1536) |
| Векторное хранилище | PostgreSQL + pgvector (HNSW, косинус) |
| База оборудования | PostgreSQL (таблица equipment) |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit (русский) |
| Оценка качества | RAGAS |
| Инфраструктура | Docker Compose (postgres + api + frontend) |

## Быстрый старт (Docker Compose)

```bash
cp .env.example .env
# Заполните OPENAI_API_KEY; при необходимости измените POSTGRES_PASSWORD

docker compose up --build
# API:      http://localhost:8000/docs
# Frontend: http://localhost:8501
```

Postgres при первом запуске автоматически создаёт схему и наполняет таблицу оборудования
тестовыми данными (`docker/init.sql`). При изменении `init.sql` пересоздайте БД:

```bash
docker compose down -v && docker compose up --build
```

Загрузка документации: через сайдбар в UI или `POST /api/v1/ingest`.

## Запуск без Docker

Нужен запущенный PostgreSQL с расширением pgvector. Проще поднять только БД через Docker:

```bash
docker compose up -d postgres

python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env              # OPENAI_API_KEY + POSTGRES_DSN (host=localhost)

make dev        # терминал 1: API
make frontend   # терминал 2: Streamlit
```

## Примеры запросов к API

```bash
# Данные оборудования (seed)
curl http://localhost:8000/api/v1/equipment/ТМ-630/10-2

# Агент — многошаговый сценарий
curl -X POST http://localhost:8000/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"question":"Трансформатор ТМ-630/10-2 давно не осматривался — что делать?"}'

# Чистый RAG (для сравнения)
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Какова периодичность осмотра масляного трансформатора?"}'
```

## Структура проекта

```
src/
├── agent/        # LLM-агент: tools, prompt, agent (AgentExecutor), service (трейс), exceptions
├── db/           # PostgreSQL: пул соединений (+pgvector), репозиторий оборудования
├── rag/          # RAG-конвейер: loader, chunker, embedder, vector_store (pgvector), retriever, generator, pipeline
├── api/          # FastAPI: роуты (agent, equipment, query, ingest, health), схемы, зависимости
└── eval/         # RAGAS-оценка качества RAG
frontend/         # Streamlit: чат с переключением режимов «агент / чистый RAG»
docker/init.sql   # Схема БД + seed-данные оборудования
configs/          # YAML-конфиги для свипа по chunk_size (оценка)
tests/            # unit + integration (55 тестов)
```

## Оценка качества (RAGAS)

```bash
# Загрузить документы и прогнать оценку
python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml --ingest-docs data/docs/
```

Метрики: faithfulness, answer_relevancy, context_recall, context_precision. Конфиги
`v1/v2/v3` задают разные размеры чанков (256/512/1024) для сравнительного эксперимента.

## Тесты и линт

```bash
make test       # 55 тестов (pytest), все на моках — БД не требуется
make lint       # ruff + mypy
```

## Корпус документации

Ядро корпуса RAG (PDF в `data/docs/`): ГОСТ 18322-2016, ГОСТ 20911-89,
РД 34.45-51.300-97 / СТО 34.01-23.1-001-2017, ГОСТ Р ИСО 13381-1-2016, ГОСТ Р 27.606-2013,
учебное пособие Хальясмаа (УрФУ). До загрузки корпуса система работает с любым тест-PDF.
