"""Проверка качества извлечения текста из PDF перед загрузкой в систему.

Использование:
    python check_pdf.py data/docs/файл.pdf

Покажет число страниц, объём текста и образец. Если в образце «глифы» вида
/G20/GE3..., значит у PDF битая кодировка шрифта (нет таблицы Unicode) — такой
документ RAG прочитать не сможет, нужна другая версия PDF.
"""
import sys
from pathlib import Path

from src.rag.loader import load_pdf


def main() -> None:
    if len(sys.argv) < 2:
        print("Укажите путь к PDF: python check_pdf.py <файл.pdf>")
        sys.exit(1)

    path = Path(sys.argv[1])
    docs = load_pdf(path)
    full = "\n".join(d.page_content for d in docs)

    glyphs = full.count("/G")
    letters = sum(c.isalpha() and c.lower() in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" for c in full)

    print(f"Файл: {path.name}")
    print(f"Страниц: {len(docs)}")
    print(f"Всего символов: {len(full)}")
    print(f"Кириллических букв: {letters}")
    print(f"Глиф-маркеров '/G': {glyphs}")
    print("-" * 60)
    if glyphs > letters:
        print("ВЕРДИКТ: ПЛОХО — текст извлекается как глифы (битая кодировка).")
        print("Нужна другая версия PDF (с нормальным текстовым слоем).")
    elif letters < 500:
        print("ВЕРДИКТ: ПОДОЗРИТЕЛЬНО — мало текста (возможно скан).")
    else:
        print("ВЕРДИКТ: ОК — текст читается, можно загружать.")
    print("-" * 60)
    print("Образец текста (первые 600 символов):\n")
    print(full[:600])


if __name__ == "__main__":
    main()
