from langchain_core.documents import Document

from src.rag.chunker import chunk_documents


def _make_docs(texts: list[str], source: str = "test.pdf") -> list[Document]:
    return [
        Document(page_content=text, metadata={"source": source, "page": i})
        for i, text in enumerate(texts)
    ]


def test_chunk_count_increases_with_long_text():
    long_text = "word " * 500  # ~2500 chars, well above chunk_size=1000
    docs = _make_docs([long_text])
    chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=200)
    assert len(chunks) > 1


def test_metadata_propagated_to_chunks():
    long_text = "sentence. " * 200
    docs = _make_docs([long_text], source="my_doc.pdf")
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)

    for chunk in chunks:
        assert chunk.metadata.get("source") == "my_doc.pdf"
        assert "page" in chunk.metadata


def test_short_doc_stays_single_chunk():
    short_text = "This is a short document."
    docs = _make_docs([short_text])
    chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=200)
    assert len(chunks) == 1
    assert chunks[0].page_content == short_text


def test_chunk_size_respected():
    long_text = "a" * 3000
    docs = _make_docs([long_text])
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    for chunk in chunks:
        # chunks may slightly exceed due to separator logic, but should be close
        assert len(chunk.page_content) <= 600


def test_empty_docs_returns_empty():
    result = chunk_documents([], chunk_size=1000, chunk_overlap=200)
    assert result == []


def test_multiple_docs_all_get_chunked():
    docs = _make_docs(["word " * 300, "word " * 300], source="multi.pdf")
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 2
