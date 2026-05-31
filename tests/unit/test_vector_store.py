import threading
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document

from src.rag.vector_store import PgVectorStore


def _make_chunks(n: int = 3) -> list[Document]:
    return [
        Document(
            page_content=f"Фрагмент {i} о теме {i}.",
            metadata={"source": "test.pdf", "page": i},
        )
        for i in range(n)
    ]


def _make_pool():
    """Мок пула: pool.connection() и conn.cursor() — контекст-менеджеры."""
    cursor = MagicMock()
    cursor.fetchone.return_value = (0,)
    cursor.fetchall.return_value = []
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = conn
    return pool, conn, cursor


@pytest.fixture
def mock_store():
    pool, conn, cursor = _make_pool()
    embedder = MagicMock()
    embedder.embed_documents.return_value = [[0.0] * 1536] * 5
    embedder.embed_query.return_value = [0.0] * 1536

    store = PgVectorStore.__new__(PgVectorStore)
    store._expected_dim = 1536
    store._embedder = embedder
    store._pool = pool
    store._lock = threading.Lock()
    store._cached_index_size = 0
    store._is_ready = False

    yield store, cursor, embedder


def test_is_loaded_false_when_empty(mock_store):
    store, _, _ = mock_store
    store._is_ready = False
    assert not store.is_loaded


def test_is_loaded_true_when_vectors_exist(mock_store):
    store, _, _ = mock_store
    store._is_ready = True
    assert store.is_loaded


def test_add_documents_executes_upsert(mock_store):
    store, cursor, embedder = mock_store
    embedder.embed_documents.return_value = [[0.1] * 1536]
    store.add_documents(_make_chunks(1))
    assert cursor.executemany.called


def test_add_documents_row_count(mock_store):
    store, cursor, embedder = mock_store
    embedder.embed_documents.return_value = [[0.0] * 1536] * 3
    store.add_documents(_make_chunks(3))
    rows = cursor.executemany.call_args.args[1]
    assert len(rows) == 3


def test_add_documents_row_fields(mock_store):
    store, cursor, embedder = mock_store
    embedder.embed_documents.return_value = [[0.0] * 1536]
    store.add_documents(_make_chunks(1))
    rows = cursor.executemany.call_args.args[1]
    # (id, doc_id, source, page, text, embedding)
    row = rows[0]
    assert len(row) == 6
    assert row[2] == "test.pdf"          # source
    assert row[4].startswith("Фрагмент")  # text
    assert isinstance(row[5], str) and row[5].startswith("[")  # vector-литерал


def test_add_documents_id_differs_by_source(mock_store):
    store, cursor, embedder = mock_store
    embedder.embed_documents.return_value = [[0.0] * 1536] * 2
    chunks = [
        Document(page_content="один текст", metadata={"source": "a.pdf", "page": 1}),
        Document(page_content="один текст", metadata={"source": "b.pdf", "page": 1}),
    ]
    store.add_documents(chunks)
    rows = cursor.executemany.call_args.args[1]
    ids = [r[0] for r in rows]
    assert ids[0] != ids[1]


def test_similarity_search_returns_documents(mock_store):
    store, cursor, _ = mock_store
    # (text, source, page, score)
    cursor.fetchall.return_value = [
        ("foo", "a.pdf", 1, 0.9),
        ("bar", "b.pdf", 2, 0.7),
    ]
    results = store.similarity_search_with_score("тест", k=2)
    assert len(results) == 2
    assert all(isinstance(doc, Document) for doc, _ in results)
    assert results[0][0].metadata["source"] == "a.pdf"


def test_similarity_search_score_passthrough(mock_store):
    store, cursor, _ = mock_store
    cursor.fetchall.return_value = [("foo", "a.pdf", 1, 0.83)]
    results = store.similarity_search_with_score("q", k=1)
    _, score = results[0]
    assert abs(score - 0.83) < 1e-6


def test_index_size_returns_cached(mock_store):
    store, _, _ = mock_store
    store._cached_index_size = 42
    assert store.index_size == 42


def test_clear_namespace_truncates(mock_store):
    store, cursor, _ = mock_store
    store.clear_namespace()
    executed_sql = " ".join(str(c.args[0]) for c in cursor.execute.call_args_list)
    assert "TRUNCATE" in executed_sql.upper()
    assert store.index_size == 0
