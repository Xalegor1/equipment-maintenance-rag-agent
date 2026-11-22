# Архитектура

## Поток запроса

```
Клиент (Streamlit / curl)
  │
  ▼
FastAPI  /api/v1/agent
  │
  ├─ валидация схемы (Pydantic)
  ├─ AgentService → LangChain ReAct AgentExecutor
  │     ├─ промпт: роль, правила атрибуции, «нет ответа — скажи прямо»
  │     ├─ tool search_documentation(query)
  │     │     └─ гибридный retrieval: dense (pgvector/HNSW) + FTS(tsvector), слияние и порог
  │     └─ tool query_equipment_db(equipment_id)
  │           └─ репозиторий PostgreSQL: даты ТО, параметры, расчёт просрочки
  └─ ответ: текст + источники (файл, страница, цитата)
```

## RAG-конвейер

`loader` (pypdf) → `chunker` (RecursiveCharacterTextSplitter, русские границы
предложений) → `embedder` (OpenAI, батчи по 100) → `vector_store` (pgvector,
HNSW, косинус) → `retriever` (dense + лексический поиск, объединение) →
`generator` (ответ строго по найденным фрагментам).

## Данные

```
documents ──< document_chunks (vector(1536), tsv, HNSW)
equipment (seed в docker/init.sql)
```

`init.sql` создаёт схему, расширение `vector` и демо-записи. Полный сброс —
`docker compose down -v`.

## Оценка

`src/eval` прогоняет RAGAS-метрики по тестсету и логирует эксперименты (chunk_size
256/512/1024) отдельными YAML-конфигами. Тестсет генерируется
`src/eval/testset_generator.py` по загруженному корпусу.

## Инфраструктура

Три контейнера: `postgres` (pgvector), `api` (FastAPI), `frontend` (Streamlit).
Секреты — только через `.env`, в репозиторий попадает `.env.example`.
