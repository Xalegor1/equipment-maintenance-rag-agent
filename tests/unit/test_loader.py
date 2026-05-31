import pytest

from src.rag.loader import load_pdf


def test_load_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_pdf("/nonexistent/path/file.pdf")


def test_load_pdf_wrong_extension(tmp_path):
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("hello")
    with pytest.raises(ValueError, match=".txt"):
        load_pdf(txt_file)


def test_load_pdf_returns_documents(sample_pdf_path):
    docs = load_pdf(sample_pdf_path)
    assert len(docs) >= 1
    for doc in docs:
        assert "source" in doc.metadata
        assert "page" in doc.metadata
        assert isinstance(doc.page_content, str)


def test_load_pdf_source_is_filename(sample_pdf_path):
    docs = load_pdf(sample_pdf_path)
    for doc in docs:
        assert doc.metadata["source"] == sample_pdf_path.name
