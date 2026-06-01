import re
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

_MAX_PAGES = 500


def clean_gost_text(text: str) -> str:
    """Лёгкая очистка текста русских нормативных документов после PyPDFLoader:
    убирает колонтитулы с обозначением ГОСТа, одиночные номера страниц, дефисные
    переносы слов и схлопывает лишние пустые строки."""
    # PostgreSQL text не допускает NUL-байты (встречаются в извлечённом тексте PDF)
    text = text.replace("\x00", "")
    # Дефисный перенос слова на границе строки: "тех-\nническое" -> "техническое"
    text = re.sub(r"-\n(\s*)", "", text)
    # Колонтитул с обозначением стандарта: "ГОСТ 18322-2016", "ГОСТ Р 58058-2018"
    text = re.sub(r"ГОСТ\s+Р?\s*[\d\.\-–—]+", "", text)
    # Одиночный номер страницы на отдельной строке
    text = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", text)
    # Более двух пустых строк подряд -> одна пустая
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf(path: str | Path) -> list[Document]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF не найден: {path}")
    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"Ожидался файл .pdf, получено: {path.suffix}")

    loader = PyPDFLoader(str(path))
    docs = loader.load()

    if len(docs) > _MAX_PAGES:
        raise ValueError(f"PDF превышает лимит в {_MAX_PAGES} страниц ({len(docs)} стр.).")

    # Единые ключи метаданных + очистка текста на всех страницах
    for doc in docs:
        doc.page_content = clean_gost_text(doc.page_content)
        doc.metadata["source"] = path.name
        doc.metadata["page"] = doc.metadata.get("page", 0) + 1

    return docs
