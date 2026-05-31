from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Сепараторы под структуру русских нормативных документов (ГОСТ/РД):
# сначала разрыв между разделами, затем перед нумерованным пунктом (5.2.1),
# далее обычные границы строки/слова.
_SEPARATORS = [
    "\n\n",            # пустая строка — между разделами
    r"\n(?=\d+\.\d)",  # перед нумерованным пунктом: "\n5.2", "\n5.2.1"
    "\n",
    " ",
    "",
]


def chunk_documents(
    docs: list[Document],
    chunk_size: int = 1500,
    chunk_overlap: int = 300,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=_SEPARATORS,
        is_separator_regex=True,
        length_function=len,
    )
    # split_documents (не split_text) переносит Document.metadata в дочерние чанки
    chunks = splitter.split_documents(docs)
    return chunks
