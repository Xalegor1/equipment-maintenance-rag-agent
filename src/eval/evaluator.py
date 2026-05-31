import json
import time
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

from src.rag.config import Settings, get_settings
from src.rag.pipeline import RAGPipeline

DEFAULT_METRICS = [faithfulness, answer_relevancy, context_recall, context_precision]


def run_evaluation(
    testset_path: Path,
    pipeline: RAGPipeline,
    metrics: list | None = None,
    settings: Settings | None = None,
) -> dict[str, float]:
    if metrics is None:
        metrics = DEFAULT_METRICS

    if settings is None:
        settings = get_settings()

    judge_llm = LangchainLLMWrapper(ChatOpenAI(
        model=settings.openai_chat_model,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    ))
    judge_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    ))
    for metric in metrics:
        metric.llm = judge_llm
        if hasattr(metric, "embeddings"):
            metric.embeddings = judge_embeddings

    with open(testset_path, encoding="utf-8") as f:
        records = json.load(f)

    samples = []
    latencies: list[float] = []

    for record in records:
        question = record["question"]
        ground_truth = record.get("ground_truth", record.get("reference", ""))
        if isinstance(ground_truth, list):
            ground_truth = ground_truth[0] if ground_truth else ""

        start = time.perf_counter()
        result = pipeline.query(question)
        latencies.append((time.perf_counter() - start) * 1000)

        samples.append(SingleTurnSample(
            user_input=question,
            response=result["answer"],
            retrieved_contexts=[c.get("full_text") or c.get("excerpt") or "" for c in result["citations"]],
            reference=ground_truth,
        ))

    dataset = EvaluationDataset(samples=samples)
    scores = evaluate(dataset, metrics=metrics)
    scores_df = scores.to_pandas()
    metric_cols = [m.name for m in metrics]
    result_dict = {col: round(float(scores_df[col].mean()), 4) for col in metric_cols if col in scores_df.columns}
    result_dict["latency_ms_avg"] = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    result_dict["_num_questions"] = len(records)

    return result_dict
