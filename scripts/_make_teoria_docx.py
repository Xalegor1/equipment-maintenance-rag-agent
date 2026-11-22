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


def voice(label, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    r = p.add_run(label + ' '); r.bold = True; r.font.color.rgb = GREEN
    r2 = p.add_run(text); r2.italic = True
    p.paragraph_format.space_after = Pt(4)


def add_table(rows, widths=None):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = 'Light Grid Accent 1'
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, txt in enumerate(zip(cells, row)):
            cell, val = txt
            run = cell.paragraphs[0].add_run(val)
            run.font.size = Pt(9.5)
            if i == 0:
                run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif j == 0:
                run.bold = True


# --- Title
title = doc.add_paragraph()
tr = title.add_run('Шпаргалка: ТЕОРИЯ')
tr.bold = True; tr.font.size = Pt(20); tr.font.color.rgb = NAVY
sub = doc.add_paragraph()
sr = sub.add_run('Защита курсовой — ИСППР по техобслуживанию (LLM-агент + RAG) · Еловенко Е.Е., ИСТ-АМО-203Б')
sr.font.size = Pt(9.5); sr.font.color.rgb = GREY
note = doc.add_paragraph()
nr = note.add_run('Каждый блок: простое объяснение вслух (зелёным) + точные факты — авторы, годы, цифры.')
nr.font.size = Pt(9.5); nr.italic = True; nr.font.color.rgb = GREY
doc.add_paragraph()

# 1
h2('1. СППР (DSS) и зачем тут LLM')
voice('Вслух:', 'СППР — интерактивная система, помогающая принимать решения в слабоструктурированных задачах. Три подсистемы: данные, модели, интерфейс. LLM меняет интерфейс — вместо SQL диалог на естественном языке, и часть «движка» (подбор источников, синтез) берёт на себя модель.')
para([('Моя СППР', True), (' = информационно-аналитическая (Data-Driven DSS). ЛПР — инженер-оператор / начальник смены. Два класса знаний: ', False), ('семантические', True), (' (нормативка) и ', False), ('фактологические', True), (' (состояние парка).', False)])
h3('Ограничения «голой» LLM → почему нужен RAG')
para('знания ограничены датой обучения (cutoff), нет корпоративных данных;', bullet=True)
para('галлюцинации — правдоподобная, но неверная информация;', bullet=True)
para('нет доступа к актуальному состоянию объектов;', bullet=True)
para('нельзя класть конфиденциальные документы в обучающую выборку.', bullet=True)
para('→ RAG: документы во внешнем хранилище, подключаются только в момент запроса.')

# 2
h2('2. RAG — Retrieval-Augmented Generation')
voice('Вслух:', 'Модель получает на вход не только вопрос, но и релевантные куски документов, найденные поиском. Это даёт работу с корпоративными данными без дообучения модели.')
para([('Автор: ', True), ('П. Льюис (Lewis P.) и соавт., 2020.', False)])
para([('Три поколения (обзор Gao Y., 2023): ', True), ('Naive (embed→search→generate) · Advanced (переформулировка, переранжирование, фильтрация) · Modular (агент, function calling, несколько источников).', False)])
para([('Я выбрал Modular RAG', True), (' — нужен агент, работающий с двумя источниками (документы + база парка).', False)])

# 3
h2('3. ReAct — Reasoning + Acting')
voice('Вслух:', 'Агент рассуждает и действует пошагово: мысль (Thought) → действие/вызов инструмента (Action) → результат (Observation), и так по кругу, пока не соберёт достаточно для ответа.')
para([('Авторы: ', True), ('Ш. Яо (Yao S.) и соавт., 2022. Превосходит чистый Chain-of-Thought, где нужны внешние источники.', False)])
para([('В моей системе: ', True), ('нативный function calling LangChain (а не хрупкий текстовый парсинг Action/Observation). Трасса шагов — через intermediate_steps.', False)])

# 4
h2('4. Гибридный поиск')
voice('Вслух:', 'Объединяю два поиска. Плотный (векторный) понимает смысл и синонимы, но «размывается» на лишних словах. Лексический (полнотекстовый) ловит точные термины, но пропускает синонимы. Вместе компенсируют слабости друг друга.')
add_table([
    ('Метод', 'Принцип', 'Слабость'),
    ('Плотный (dense)', 'косинус эмбеддингов', 'семантическое размытие на «шумных» запросах'),
    ('Лексический (sparse)', 'FTS, ts_rank', 'пропускает синонимы и парафразы'),
    ('Гибрид с RRF', 'слияние по обратным рангам', 'сложнее реализация, два индекса'),
])
para([('Семантическое размытие (semantic dilution): ', True), ('при куче слабосвязанных слов эмбеддинг — усреднённая точка, далёкая от конкретного фрагмента. Пример: «осмотр трансформатор масляный силовой» — п. 2.1.34 ПТЭЭП (с.53) выпадал за топ-15; по теме «периодичность осмотра трансформаторов без отключения» — встаёт на 1 место.', False)])

# 5
h2('5. RRF — Reciprocal Rank Fusion')
voice('Вслух:', 'Слияние двух списков по позициям (рангам), а не по «сырым» оценкам. В этом сила — косинус и tf-idf несравнимы напрямую, а ранги сравнимы.')
para([('Формула: ', True), ('RRF(d) = Σ 1 / (k + rankᵢ(d)); k — сглаживание, у меня k = 60.', False)])
para([('Авторы: ', True), ('Cormack G., Clarke, Buettcher, 2009.', False)])
para([('Почему RRF: ', True), ('не требует единой шкалы оценок и размеченной выборки — идеально для прототипа.', False)])

# 6
h2('6. pgvector + HNSW')
voice('Вслух:', 'pgvector — расширение PostgreSQL для векторов и поиска по близости, оператор <=> — косинусное расстояние. Чтобы не сканировать всё, строится индекс HNSW.')
para([('HNSW', True), (' (Malkov, Yashunin, 2020) — многоуровневый граф: верх для грубой навигации, низ для точного уточнения. Параметры m (рёбер на вершину) и ef_construction (качество ↔ память).', False)])
para([('Лексическая ветка: ', True), ('tsvector + GIN-индекс, русский словарь (ispell + snowball), ts_rank_cd.', False)])

# 7
h2('7. Конвейер обработки документов (RAG-pipeline)')
para('Загрузка PDF — PyPDFLoader.', bullet=True)
para('Очистка — колонтитулы, переносы, лишние пробелы.', bullet=True)
para('Чанкинг — RecursiveCharacterTextSplitter, до 1500 символов, overlap 300; для ГОСТ/РД регулярка держит пункт целиком.', bullet=True)
para('Эмбеддинги — text-embedding-3-small, размерность 1536, пакетами по 100.', bullet=True)
para('Запись в БД, id = SHA-256 содержимого → идемпотентность.', bullet=True)

# 8
h2('8. Нормативная база (предметная)')
add_table([
    ('Документ', 'Что регламентирует'),
    ('ГОСТ 18322-2016', 'термины и определения ТОиР'),
    ('ГОСТ 20911-89', 'техническая диагностика, термины'),
    ('ПТЭЭП', 'правила тех. эксплуатации; п. 2.1.34 — осмотр трансформаторов не реже 1 раза в месяц'),
    ('РД 34.45-51.300-97', 'объём и нормы испытаний электрооборудования'),
    ('ГОСТ Р 71853-2024', 'удалённый мониторинг и диагностика энергооборудования (с 2025)'),
])
para([('Ключевая мысль: ', True), ('два вида знаний → архитектура из RAG по документам + запросов к БД парка.', False)])

# 9
h2('9. Архитектура системы (4 слоя)')
para('Представление — Streamlit (чат + трасса ReAct).', bullet=True)
para('Прикладная логика — FastAPI (маршрутизация).', bullet=True)
para('Агент — LangChain, gpt-4o-mini, function calling, 2 инструмента.', bullet=True)
para('Данные — PostgreSQL 16 + pgvector (векторы фрагментов + таблица equipment).', bullet=True)

# 10
h2('10. Почему расчёт просрочки — в коде, а не в LLM')
voice('Вслух:', 'Модели плохо считают арифметику с датами. Поэтому сравнение дат делает код инструмента query_equipment_db детерминированно, а модель занимается только языком. Общий принцип надёжных агентов: вычисления — в коде, язык — в модели.')

# Anchors
h2('Цифры-якоря (держать в голове)')
para('2 документа, 938 фрагментов, 12 единиц оборудования.', bullet=True)
para('Эталон: трансформатор ТМ-630/10-2, последний осмотр 14.08.2024, ТП-1.', bullet=True)
para('RRF k = 60; чанк 1500 / overlap 300; эмбеддинг 1536.', bullet=True)
para('Модель gpt-4o-mini, temperature 0. · 60 автотестов.', bullet=True)
para('Время ответа: факт. ~4–5 с, нормативный ~6–9 с, комбинированный ~8–15 с.', bullet=True)

out = r'C:\Word_projects\Шпаргалка_теория_ИСППР_Еловенко.docx'
doc.save(out)
print('SAVED:', out)
