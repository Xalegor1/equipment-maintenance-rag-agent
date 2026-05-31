"""
Generate a RAGAS synthetic Q&A testset from PDF documents.

Run ONCE locally, commit data/eval/testset.json — never run in CI.
Cost: ~$0.10-0.30 in OpenAI API credits for 20 questions.
"""
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset import TestsetGenerator

from src.rag.config import get_settings


def generate_testset(
    docs_dir: Path,
    output_path: Path,
    num_questions: int = 20,
) -> None:
    settings = get_settings()

    all_docs = []
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {docs_dir}")

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        all_docs.extend(loader.load())

    print(f"Loaded {len(all_docs)} pages from {len(pdf_files)} PDFs")

    llm = LangchainLLMWrapper(ChatOpenAI(
        model=settings.openai_chat_model,
        openai_api_key=settings.openai_api_key,
    ))
    embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key,
    ))

    generator = TestsetGenerator(llm=llm, embedding_model=embeddings)
    testset = generator.generate_with_langchain_docs(all_docs, testset_size=num_questions)

    df = testset.to_pandas()

    # RAGAS 0.2.x uses user_input/reference; rename to question/ground_truth for evaluator
    df = df.rename(columns={"user_input": "question", "reference": "ground_truth"})
    df = df[["question", "ground_truth"]]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(output_path, orient="records", indent=2, force_ascii=False)
    print(f"Saved {len(df)} questions to {output_path}")


if __name__ == "__main__":
    generate_testset(
        docs_dir=Path("data/eval/sample_docs"),
        output_path=Path("data/eval/testset.json"),
        num_questions=20,
    )
