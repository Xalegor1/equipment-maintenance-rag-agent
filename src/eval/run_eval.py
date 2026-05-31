"""
CLI-запуск RAGAS-оценки.

Использование:
    python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml
    python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml --ingest-docs data/docs/
"""
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from src.eval.evaluator import run_evaluation
from src.rag.config import Settings
from src.rag.pipeline import RAGPipeline
from src.rag.vector_store import PgVectorStore


def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Запуск RAGAS-оценки RAG-конвейера.")
    parser.add_argument("--config", required=True, type=Path, help="Путь к YAML-конфигу оценки")
    parser.add_argument(
        "--testset",
        type=Path,
        default=Path("data/eval/testset.json"),
        help="Путь к JSON с тест-вопросами",
    )
    parser.add_argument(
        "--ingest-docs",
        type=Path,
        default=None,
        dest="ingest_docs",
        help="PDF или каталог PDF для загрузки перед оценкой. Очищает хранилище — "
             "используй для контролируемого свипа по chunk_size.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Опционально: путь для сохранения метрик в JSON",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"ОШИБКА: конфиг не найден: {args.config}")
        sys.exit(1)
    if not args.testset.exists():
        print(f"ОШИБКА: тест-сет не найден: {args.testset}")
        print("Сначала запусти src/eval/testset_generator.py (локально).")
        sys.exit(1)

    config = load_config(args.config)

    settings = Settings(
        chunk_size=config.get("chunk_size", 1500),
        chunk_overlap=config.get("chunk_overlap", 300),
        retrieval_top_k=config.get("top_k", 4),
        openai_chat_model=config.get("model", "gpt-4o-mini"),
        openai_embedding_model=config.get("embedding_model", "text-embedding-3-small"),
    )

    os.environ.setdefault("RAGAS_MAX_WORKERS", "1")

    print(f"Оценка по конфигу: {args.config}")
    print(f"  chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap}, top_k={settings.retrieval_top_k}")

    pipeline = RAGPipeline(settings)

    if args.ingest_docs:
        if args.ingest_docs.is_dir():
            pdfs = sorted(args.ingest_docs.glob("*.pdf"))
        else:
            pdfs = [args.ingest_docs]

        if not pdfs:
            print(f"ОШИБКА: PDF-файлы не найдены в {args.ingest_docs}")
            sys.exit(1)

        if isinstance(pipeline._store, PgVectorStore):
            print("Очистка хранилища перед загрузкой...")
            pipeline._store.clear_namespace()

        print(f"Загрузка {len(pdfs)} документ(ов)...")
        for pdf in pdfs:
            print(f"  {pdf.name}")
            pipeline.ingest(pdf)
        print(f"Размер индекса после загрузки: {pipeline.index_size}")

    if pipeline.index_size == 0:
        print("ОШИБКА: хранилище пустое. Загрузите документы перед оценкой (--ingest-docs).")
        sys.exit(1)

    metrics = run_evaluation(testset_path=args.testset, pipeline=pipeline, settings=settings)
    num_questions = int(metrics.pop("_num_questions", 0))

    # Таблица результатов
    print("\n" + "=" * 50)
    print(f"Вопросов в тест-сете: {num_questions}")
    print("-" * 50)
    print(f"{'Метрика':<30} {'Значение':>10}")
    print("-" * 50)
    for k, v in metrics.items():
        print(f"{k:<30} {v:>10.4f}")
    print("=" * 50)

    if args.out:
        payload = {"config": str(args.config), "num_questions": num_questions, "metrics": metrics}
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Метрики сохранены: {args.out}")

    # Проверка порогов — выход 1 при недоборе (для CI)
    thresholds = config.get("thresholds", {})
    failures = []
    for metric, threshold in thresholds.items():
        actual = metrics.get(metric, 0.0)
        if actual < threshold:
            failures.append(f"{metric}: {actual:.4f} < {threshold} (порог)")

    if failures:
        print("\nНЕ пройдены пороги:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)

    print("\nВсе пороги пройдены.")


if __name__ == "__main__":
    main()
