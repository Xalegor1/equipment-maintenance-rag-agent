# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, RGBColor, Inches

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GREEN = RGBColor(0x1B, 0x5E, 0x20)
GREY = RGBColor(0x55, 0x55, 0x55)


def h2(t):
    p = doc.add_paragraph()
    r = p.add_run(t); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = NAVY
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(3)


def h3(t):
    p = doc.add_paragraph()
    r = p.add_run(t); r.bold = True; r.font.size = Pt(11.5); r.font.color.rgb = GREEN
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)


def para(runs, bullet=False, space=2):
    p = doc.add_paragraph(style='List Bullet' if bullet else None)
    if isinstance(runs, str):
        runs = [(runs, False)]
    for text, bold in runs:
        r = p.add_run(text); r.bold = bold
    p.paragraph_format.space_after = Pt(space)


def quote(t):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(t); r.italic = True; r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p.paragraph_format.space_after = Pt(6)


title = doc.add_paragraph()
tr = title.add_run('Шпаргалка: АНАЛОГИ')
tr.bold = True; tr.font.size = Pt(20); tr.font.color.rgb = NAVY
sub = doc.add_paragraph()
sr = sub.add_run('Защита курсовой — ИСППР по техобслуживанию (LLM-агент + RAG) · Еловенко Е.Е., ИСТ-АМО-203Б')
sr.font.size = Pt(9.5); sr.font.color.rgb = GREY
doc.add_paragraph()

h2('Ответ вслух (если спросят «есть ли аналоги»)')
para([('Да, идея востребована — вендоры пошли туда же в 2023–2025. Ближайшие — генеративные ассистенты обслуживания: ', False),
      ('IBM Maximo AI Assist, Siemens Industrial Copilot, Aquant Service Co-Pilot', True),
      ('. Все — LLM поверх руководств и данных об оборудовании, ответ на естественном языке со ссылкой на источник.', False)])
para([('Моё отличие (3 вещи): ', True),
      ('российская нормативка (ПТЭЭП, РД, ГОСТ) • расчёт просрочки детерминированно в КОДЕ, не моделью • открытый прототип под GigaChat/YandexGPT для закрытого контура. Западные — закрытые, часть ушла с РФ-рынка.', False)])

h2('4 группы аналогов')
rows = [
    ('Группа', 'Примеры', 'Почему не моё'),
    ('APM-платформы (датчики)', 'IBM Maximo, Siemens Senseye, Hitachi Lumada, GE Vernova, ABB Genix', 'про датчики/временные ряды, не документы; ушли с РФ'),
    ('Ген-ассистенты (ближе всего)', 'Maximo AI Assist, Siemens Industrial Copilot, Aquant Co-Pilot, MS Copilot Field Service', 'западные, закрытые, не РФ-норматив, расчёт не детерминирован'),
    ('Открытые RAG-фреймворки', 'PrivateGPT, RAGFlow, Verba', 'нет учёта оборудования и регламентных сроков'),
    ('ТОиР-системы', 'ТРИМ, 1С:ТОиР, Galaktika EAM', 'нет диалога по нормативке'),
]
table = doc.add_table(rows=0, cols=3)
table.style = 'Light Grid Accent 1'
for i, (a, b, c) in enumerate(rows):
    cells = table.add_row().cells
    for j, (cell, txt) in enumerate(zip(cells, (a, b, c))):
        rp = cell.paragraphs[0]; run = rp.add_run(txt)
        run.font.size = Pt(9.5)
        if i == 0:
            run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        elif j == 0:
            run.bold = True
para([('Фраза-вывод: ', True),
      ('моя ниша на пересечении — RAG по нормативке + данные парка + детерминированный расчёт. Ни одна из 4 групп её не закрывает.', False)], space=6)

h2('Ссылки (официальные страницы)')
links = [
    'Aquant Service Co-Pilot — https://www.aquant.ai/   ← ОТКРЫТЬ ЗАРАНЕЕ',
    'Siemens Industrial Copilot — https://www.siemens.com/global/en/products/automation/topic-areas/industrial-copilot.html',
    'IBM Maximo (Assist) — https://www.ibm.com/products/maximo',
    'MS Copilot for Dynamics 365 Field Service — https://www.microsoft.com/en-us/dynamics-365/products/field-service',
    'PrivateGPT (открытый, GitHub) — https://github.com/zylon-ai/private-gpt',
    'RAGFlow (открытый, GitHub) — https://github.com/infiniflow/ragflow',
    '1С:ТОиР — https://solutions.1c.ru/catalog/toir2-corp',
]
for l in links:
    para(l, bullet=True)
para([('Открывать заранее: ', True), ('Aquant', True),
      (' (попадание в тему — agentic AI для обслуживания оборудования; клиенты Siemens, Stryker). Запасная вкладка — Siemens. [проверено 22.06.2026 — обе живые]', False)])

h3('Что сказать по открытому сайту (Aquant)')
quote('«Вот ближайший по логике аналог — Aquant Service Co-Pilot. Это агентный ИИ поверх сервисных мануалов и данных: техник задаёт вопрос — система отвечает по документации в реальном времени. Та же логика, что у меня в инструменте search_documentation. Но Aquant — закрытая западная платформа, не работает с российской нормативкой (ПТЭЭП, РД, ГОСТ) и не считает регламентную просрочку по парку детерминированно в коде. У меня обе эти вещи есть, и прототип открытый — под замену на GigaChat/YandexGPT.»')

h3('Если откроешь Siemens вместо/вдобавок')
quote('«Siemens тоже пошёл в Industrial AI — агенты для инжиниринга и обслуживания поверх своих систем. Подтверждает, что направление востребовано. Но это закрытая платформа под оборудование Siemens, не РФ-нормативка.»')

h2('Про живое демо аналогов')
para('Западные вживую показать НЕЛЬЗЯ — закрытые, под корпоративные внедрения. Из открытого — PrivateGPT/RAGFlow на GitHub, но они без учёта оборудования.')
para([('Мой живой «аналог» = переключатель «Агент / Чистый RAG» в моём приложении: ', True),
      ('чистый RAG = упрощённая версия конкурентов (только документы), агент = моё решение (документы + база парка + расчёт).', False)])

h2('РФ-рынок: LLM+RAG-чат — есть или нет? (важный вопрос)')
para([('Отвечать на ДВУХ уровнях — это и есть сильная позиция.', True)])
h3('Уровень 1 — технология LLM+RAG-чат по документам: НА РФ-РЫНКЕ ЕСТЬ')
para('YandexGPT Pro / Yandex AI Studio — прямо заявлен RAG-сценарий (поиск по базе знаний + генерация).', bullet=True)
para('GigaChat (Сбер), MTS AI Cotype — модели + API под чат-ассистентов по своим данным.', bullet=True)
para('Студии-интеграторы (aritin, doubletapp, allsee.team) — «ИИ-ассистент с базой знаний RAG» уже типовая услуга.', bullet=True)
para([('Вывод: ', True), ('сам паттерн «RAG-чат по своим документам» — коммодити, не новость.', False)])
h3('Уровень 2 — МОЯ комбинация как коробочный продукт: НЕТ')
para('Готового решения, где в одном: (1) RAG по российской нормативке ТО (ПТЭЭП, РД, ГОСТ) + (2) структурированная база парка + (3) детерминированный расчёт просрочки в коде — НЕТ. Есть либо generic-конструкторы (Яндекс/Сбер, без предметной модели ТОиР), либо ТОиР-системы (1С:ТОиР, без диалога по нормативке), либо ИИ-диагностика в ТОиР как заказные пилоты (Северсталь, Газпром нефть, Росатом). Коробки с моей сборкой нет — эту нишу я и занимаю.')
h3('Текст вслух — «а на РФ-рынке есть?»')
quote('«Если про технологию — LLM+RAG-чат по документам на РФ-рынке уже есть: YandexGPT Pro с RAG-сценарием, GigaChat, MTS Cotype, плюс студии делают на заказ. Но это generic-конструкторы: грузишь свои документы, предметной модели нет. Готового продукта именно с моей комбинацией — RAG по российской нормативке ТО плюс база парка плюс детерминированный расчёт просрочки в коде — на рынке нет. Только внутренние пилоты у Северстали, Газпром нефти, Росатома. Эту нишу я и занимаю.»')
h3('Если дожмут — «значит, новизна не в технологии?»')
quote('«Верно — новизна не в самом RAG, он коммодити. Новизна в сборке: соединение семантического поиска по нормативке со структурированными данными парка и детерминированным расчётом регламентной просрочки в одном диалоговом решении. Этого не закрывают ни RAG-конструкторы, ни ТОиР-системы.»')

out = r'C:\Word_projects\Шпаргалка_аналоги_ИСППР_Еловенко.docx'
doc.save(out)
print('SAVED:', out)
