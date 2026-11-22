import re
import zipfile
from pathlib import Path

path = Path("Поясн_записка_Еловенко_v4.docx")
with zipfile.ZipFile(path) as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

xml = xml.replace("</w:p>", "\n").replace("<w:br/>", "\n").replace("</w:tr>", "\n").replace("</w:tc>", " | ")
text = re.sub(r"<[^>]+>", "", xml)
text = re.sub(r"[ \t]{2,}", " ", text)
text = re.sub(r"\n{3,}", "\n\n", text).strip()

Path("_kursach.txt").write_text(text, encoding="utf-8")
print("СИМВОЛОВ:", len(text))
print("СТРОК:", text.count(chr(10)))
