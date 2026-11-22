import re
import zipfile
from pathlib import Path

path = Path("data/docs/Курсовая.docx")
with zipfile.ZipFile(path) as z:
    names = z.namelist()
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

# Преобразуем абзацы/переводы строк в \n, затем срезаем теги
xml = xml.replace("</w:p>", "\n").replace("<w:br/>", "\n").replace("</w:tr>", "\n")
text = re.sub(r"<[^>]+>", "", xml)
text = re.sub(r"\n{3,}", "\n\n", text)

print("ФАЙЛЫ В DOCX:", [n for n in names if n.startswith("word/")][:10])
print("ДЛИНА ТЕКСТА:", len(text), "символов")
print("=" * 70)
print(text.strip()[:6000])
