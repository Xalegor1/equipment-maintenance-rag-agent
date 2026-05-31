# Материалы для курсовой работы: ИСППР на основе LLM-агента для ТО высоковольтного оборудования

Ниже — структурированный отчёт по 7 разделам с конкретными источниками, ссылками и рекомендациями. Все материалы подобраны под стек Python + FastAPI + LangChain + PostgreSQL/pgvector + React + Claude API и предметную область — техническое обслуживание (ТО) высоковольтного электрооборудования.

---

## 1. Похожие курсовые и дипломные работы

### Российские ВУЗы — ВКР и магистерские диссертации

**1. Чичулин М.С. (НИУ ВШЭ, ФКН, магистратура «Машинное обучение и высоконагруженные системы», 2025)** — «Построение вопросно-ответной системы с использованием Retrieval-Augmented Generation». Стек: Llama-Chat, Qdrant, RAG-pipeline, Telegram-бот. Метрики: F1=0,83, доля галлюцинаций ≤7%, время ответа 1,2 с. Ссылка: https://www.hse.ru/edu/vkr/1049386909. **Прямой методологический аналог** — образец постановки эксперимента и оценки качества.

**2. Комарова Е.И. (НИУ ВШЭ, ФКН, 2024)** — «Оценка качества больших языковых моделей для разработки системы умного поиска в вопросно-ответной форме на базе знаний для сотрудников компании». RAG на llama_index + LoRA-дообучение. https://www.hse.ru/edu/vkr/929251410. Полезно для главы «Методы оценки качества».

**3. ВКР НИУ ВШЭ (магистратура Data Science, 2024)** — «LLM-ассистент в конкретной области» (legal-домен). Сравнение LoRA vs RAG, обоснование выбора RAG для узкого домена. https://www.hse.ru/edu/vkr/926007324. **Прямой методологический образец** для адаптации LLM к домену ТО электрооборудования.

**4. Русакова Д.В. (НИУ ВШЭ, ФКН, 2024)** — «Финансовый помощник на основе LLM». Гибрид LLM + специализированная ML-модель (LSTM). https://www.hse.ru/edu/vkr/1052910991. Полезен для обоснования гибридной архитектуры (LLM-агент + предиктивные модели).

**5. Айдова Е.П. (НИУ ВШЭ Нижний Новгород, магистратура «Интеллектуальный анализ данных»)** — «Разработка вопросно-ответной системы с использованием глубокого обучения». https://www.hse.ru/edu/vkr/473567250. База для главы «Обзор подходов».

**6. ВКР СПбПУ (ИКНТ, 2023)** — «Разработка системы поддержки принятия решений для ранжирования репозиториев GitHub». https://elib.spbstu.ru/dl/3/2023/vr/vr23-3712.pdf/info. Шаблон ИСППР: постановка задачи, архитектура, критерии.

**7. ВКР СПбПУ** — «Разработка и исследование поддержки принятия решений при отборе кандидатов и реализация её на основе технологий InterSystems». http://elib.spbstu.ru/dl/2/7861.pdf/view. Образец проектирования модулей принятия решений.

**8. ВКР СПбПУ ИЭиТС** — «Система управления и диспетчеризации инженерного оборудования многоквартирного дома». https://elib.spbstu.ru/dl/2/v17-6375.pdf/info. Применимо для проектирования модуля мониторинга.

**9. ВКР СПбПУ (2023)** — «Информационно-аналитическая поддержка развития инноваций предприятий энергетики» (кейс ПАО «ТГК-1»). https://elib.spbstu.ru/dl/3/2023/vr/vr23-604.pdf/info. Реальный кейс энергетической компании — для обоснования актуальности.

**10. ВКР СФУ (Русин М.С., рук. Легалов И.А.)** — «Бот-помощник для мессенджера Telegram». Полная пояснительная записка ВКР. https://elib.sfu-kras.ru/bitstream/handle/2311/74695/final.pdf. Шаблон оформления и структуры ВКР по чат-ботам.

**11. ВКР НИУ ВШЭ** — «Разработка чат-бота для тестирования знаний в области металлообработки» (онтологии, RDF, SKOS). https://www.hse.ru/edu/vkr/219398752. Близко к идее структурированной базы знаний.

### Учебное пособие как методическая база

**12. «Теория принятия решений и управление рисками. Модели конфликтов, неопределённости, риска» (СПбПУ, учеб. пособие)** — https://elib.spbstu.ru/dl/2/344.pdf/info. Базовая литература для теоретической главы по СППР.

### GitHub-репозитории как референсы курсовых проектов

- **mpashkovskiy/ru-rag** — RAG-pipeline для русского языка с sentence-transformers/paraphrase-multilingual-mpnet-base-v2: https://github.com/mpashkovskiy/ru-rag
- **alexeygrigorev/llm-rag-workshop** — Elasticsearch + Ollama + Streamlit: https://github.com/alexeygrigorev/llm-rag-workshop
- **IlyaGusev/rulm** — модели и инструменты для русскоязычных LLM: https://github.com/IlyaGusev/rulm

---

## 2. Академические статьи (2022-2026)

### 2.1. LLM-агенты для промышленного / предиктивного обслуживания

**[1] Harbola C., Purwar A. PARAM: Prescriptive Agents based on RAG for Automated Maintenance.** arXiv:2508.04714, 2025. https://arxiv.org/abs/2508.04714. Трёхуровневая архитектура: обнаружение аномалий → контекстный RAG-поиск → прескриптивные рекомендации. **Эталонная архитектура** «LLM-агент + RAG для обслуживания» — ближайший прямой аналог проекта.

**[2] Tao L., Huang Q., Wu X., et al. LLM-R: A Framework for Domain-Adaptive Maintenance Scheme Generation Combining Hierarchical Agents and RAG.** arXiv:2411.04476, 2024 (Beihang Univ., NTU). https://arxiv.org/abs/2411.04476. Иерархические агенты + RAG, технология LORA-KR loss. Соответствует теме курсовой почти 1-в-1.

**[3] Meng H., et al. From Prediction to Prescription: Large Language Model Agent for Context-Aware Maintenance Decision Support.** Proc. PHME (PHM Society Europe), 2024. https://papers.phmsociety.org/index.php/phme/article/download/4114/2428. Агент на GPT-4 + RAG + классификатор неисправностей; кейс — линейный актуатор. Точная схема «диагностика → RAG → LLM-агент → СППР».

**[4] Zhang Z., et al. Consultation on Industrial Machine Faults with Large Language Models.** arXiv:2410.03223, 2024. https://arxiv.org/abs/2410.03223. LLM как «второе мнение» для инженера-эксплуатационника, повышение точности диагностики.

**[5] Dimidov V., Hawlader F., Jafarnejad S., Frank R. Cleaning Maintenance Logs with LLM Agents for Improved Predictive Maintenance.** arXiv:2511.05311, 2025 (Univ. of Luxembourg, SnT). https://arxiv.org/abs/2511.05311. LLM-агенты для очистки журналов ТО — обоснование агентного подхода для подготовки данных.

### 2.2. RAG для технической документации

**[6] Lewis P., Perez E., Piktus A., et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.** NeurIPS 2020, arXiv:2005.11401. https://arxiv.org/abs/2005.11401. **Каноническая работа**, вводящая парадигму RAG. Обязательная цитата для главы про RAG.

**[7] Gao Y., Xiong Y., Gao X., et al. Retrieval-Augmented Generation for Large Language Models: A Survey.** arXiv:2312.10997, 2023. https://arxiv.org/abs/2312.10997. Самый цитируемый обзор парадигм RAG (Naive/Advanced/Modular). База для теоретической главы.

**[8] Alawadhi S., Abbas N. Optimizing Retrieval-Augmented Generation for Electrical Engineering: A Case Study on ABB Circuit Breakers.** arXiv:2505.17520, 2025 (Univ. of Leeds). https://arxiv.org/abs/2505.17520. ⭐ **Прямое попадание**: RAG + Claude API + высоковольтное оборудование (выключатели ABB). Сравнение GPT-4o, Cohere, Claude. **Ключевая статья**.

**[9] Khan A.A., Hasan M.T., Kemell K.K., Rasku J., Abrahamsson P. Developing Retrieval Augmented Generation (RAG) based LLM Systems from PDFs: An Experience Report.** arXiv:2410.15944, 2024. https://arxiv.org/abs/2410.15944. End-to-end пайплайн RAG из PDF — типовая задача курсовой.

**[10] Application of retrieval-augmented generation for interactive industrial knowledge management via a large language model.** Computer Standards & Interfaces, Elsevier, 2025. https://www.sciencedirect.com/science/article/pii/S0920548925000248. RAG для индустриального управления знаниями: BM25+эмбеддинги, MRR=88%, recall=85%.

**[11] Knowledge Graph Construction towards a Graph RAG-Enhanced Intelligent Maintenance Chatbot.** Fraunhofer Publica, 2024. https://publica.fraunhofer.de/entities/publication/08ab7acf-6787-4fe8-b089-3686a8cd1128. Альтернативный подход — Graph RAG для производственного обслуживания.

### 2.3. AI-СППР (Decision Support Systems)

**[12] Hybrid AI and LLM-Enabled Agent-Based Real-Time Decision Support Architecture for Industrial Batch Processes.** AI (MDPI), 7(2), art. 51, 2026. DOI: 10.3390/ai7020051. https://www.mdpi.com/2673-2688/7/2/51. Гибридная мультиагентная архитектура «детерминизм + LLM», минимизация галлюцинаций через структурированные правила.

**[13] DBAIOps: A Reasoning LLM-Enhanced Database Operation and Maintenance System using Knowledge Graphs.** arXiv:2508.01136, 2025. https://arxiv.org/abs/2508.01136. Реальная О&М-система для 25 СУБД, 20 промышленных сценариев (включая энергетику). Образец СППР с LLM в продакшене.

**[14] Fidma F., et al. Large Language Models for Predictive Maintenance in the Leather Tanning Industry: Multimodal Anomaly Detection in Compressors.** Electronics (MDPI), 14(10), art. 2061, 2025. DOI: 10.3390/electronics14102061. https://www.mdpi.com/2079-9292/14/10/2061. Мультимодальное слияние данных IoT-датчиков, логов и записей ТО.

### 2.4. Tool-using агенты / Function calling

**[15] Yao S., Zhao J., Yu D., et al. ReAct: Synergizing Reasoning and Acting in Language Models.** ICLR 2023, arXiv:2210.03629. https://arxiv.org/abs/2210.03629. ⭐ **Теоретическая база ReAct-агентов LangChain** — обязательная цитата.

**[16] Schick T., Dwivedi-Yu J., et al. Toolformer: Language Models Can Teach Themselves to Use Tools.** NeurIPS 2023, arXiv:2302.04761 (Meta AI). https://arxiv.org/abs/2302.04761. Концептуальная основа function calling.

**[17] Qu C., Dai S., Wei X., et al. Tool Learning with Large Language Models: A Survey.** arXiv:2405.17935, 2024. https://arxiv.org/abs/2405.17935. Систематический обзор парадигм tool learning.

**[18] Masterman T., Besen S., Sawtell M., Chao A. The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey.** arXiv:2404.11584, 2024. https://arxiv.org/abs/2404.11584. Сравнение фреймворков LangChain, AutoGen, CrewAI — для обоснования выбора LangChain.

**[19] Liu Z., et al. ToolACE: Winning the Points of LLM Function Calling.** ICLR 2025, arXiv:2409.00920. https://arxiv.org/abs/2409.00920. Berkeley Function Calling Leaderboard — для обоснования выбора модели.

### 2.5. LLM в энергетике / power systems

**[20] Jing L., Rahman A. Fault Diagnosis in Power Grids with Large Language Model.** arXiv:2407.08836, 2024 (Univ. of Malaya). https://arxiv.org/abs/2407.08836. ⭐ Применение GPT-3.5/4 + Chain-of-Thought + Tree-of-Thought для диагностики неисправностей в электросетях. **Ключевая референс-статья**.

**[21] Exploring the Capabilities and Limitations of Large Language Models in the Electric Energy Sector.** Joule (Cell Press) / arXiv:2403.09125, 2024. https://www.sciencedirect.com/science/article/pii/S254243512400237X. Обоснование RAG в электроэнергетике, обсуждение требований безопасности.

**[22] Large Language Models Integration in Smart Grids.** arXiv:2504.09059, 2025 (HEC Montreal). https://arxiv.org/abs/2504.09059. Анализ 30 реальных применений LLM в смарт-сетях по 8 категориям.

**[23] Enhancing Security and Applicability of Local LLM-Based Document Retrieval Systems in Smart Grid Isolated Environments.** Electronics (MDPI), 14(17), art. 3407, 2025. DOI: 10.3390/electronics14173407. https://www.mdpi.com/2079-9292/14/17/3407. ⭐ Полностью офлайн RAG-Q&A для подстанций, соответствие IEC 62351.

**[24] A ChatGPT-like Solution for Power Transformer Condition Monitoring.** IEEE Conf., 2024. https://ieeexplore.ieee.org/iel7/10459339/10459727/10459800.pdf. ⭐ Foundation models для прогностики силовых трансформаторов, точность 97,2%.

**[25] Chats-Grid: An Iterative Retrieval Q&A Optimization Scheme Leveraging Large Model and Retrieval Enhancement Generation in Smart Grid.** arXiv:2502.15583, 2025. https://arxiv.org/abs/2502.15583. Борьба с галлюцинациями LLM в энергетическом домене.

### Русскоязычные академические статьи

**[26] Бородулин И.В. Технология RAG (Retrieval-Augmented Generation) как инновационный подход в LLM.** КиберЛенинка, 2024. https://cyberleninka.ru/article/n/tehnologiya-rag-retrieval-augmented-generation-kak-innovatsionnyy-podhod-v-llm

**[27] Сравнительный анализ методов RAG для построения русскоязычных интеллектуальных сервисов.** КиберЛенинка. https://cyberleninka.ru/article/n/sravnitelnyy-analiz-metodov-rag-dlya-postroeniya-russkoyazychnyh-intellektualnyh-servisov

**[28] Архитектура системы предсказательного технического обслуживания сложных многообъектных систем в концепции Индустрии 4.0.** КиберЛенинка. https://cyberleninka.ru/article/n/arhitektura-sistemy-predskazatelnogo-tehnicheskogo-obsluzhivaniya-slozhnyh-mnogoobektnyh-sistem-v-kontseptsii-industrii-4-0

**[29] Методы прогнозного мониторинга технического состояния электрических машин.** КиберЛенинка. https://cyberleninka.ru/article/n/metody-prognoznogo-monitoringa-tehnicheskogo-sostoyaniya-elektricheskih-mashin

**[30] Современные решения диагностики и мониторинга высоковольтного оборудования.** КиберЛенинка. https://cyberleninka.ru/article/n/sovremennye-resheniya-diagnostiki-i-monitoringa-vysokovoltnogo-oborudovaniya

**[31] Экспертная система диагностики силовых трансформаторов.** КиберЛенинка. https://cyberleninka.ru/article/n/ekspertnaya-sistema-diagnostiki-silovyh-transformatorov

---

## 3. Похожие реализованные проекты (GitHub)

### A. RAG-системы FastAPI + LangChain + pgvector (точное совпадение со стеком)

**[1] danny-avila/rag_api** ~1.5k★. https://github.com/danny-avila/rag_api. **FastAPI + LangChain + PostgreSQL/pgvector**, async Python, поддержка OpenAI/HuggingFace/Bedrock/Ollama. Используется в LibreChat. **Эталонная реализация именно вашего стека** — взять схему хранения, разбиение по collection_name.

**[2] mazzasaverio/fastapi-langchain-rag** ~200★. https://github.com/mazzasaverio/fastapi-langchain-rag. FastAPI + LangChain (LCEL) + PGVector + Next.js + Terraform + GCP. Полноценная production-архитектура с фронтендом и деплоем.

**[3] yasaminfn/LangGraph-RAG-Agent** ~30★. https://github.com/yasaminfn/LangGraph-RAG-Agent. FastAPI + LangGraph + LangChain + PostgreSQL/pgvector + Streamlit + JWT. Мультитул-агент (PDF Q&A через RAG + OCR + Tavily web search) с persistent memory в Postgres. **Почти идеальный архитектурный аналог**.

### B. LLM-агенты с tools для БД и документов

**[4] langchain-ai/langchain-postgres** (официальный). https://github.com/langchain-ai/langchain-postgres. Канонические абстракции LangChain для Postgres: PGEngine, PGVectorStore, PostgresChatMessageHistory. **Обязательно цитировать в курсовой**.

**[5] JonathanJourney99/Postgres-SQL-Agent-Langchain.** https://github.com/JonathanJourney99/Postgres-SQL-Agent-Langchain. LangChain create_sql_agent + PostgreSQL + SQLAlchemy. Образец tool-агента, ходящего в реляционную БД (журнал ТО).

**[6] Azure-Samples/azure-postgresql-openai-langchain-autogen-demo.** https://github.com/Azure-Samples/azure-postgresql-openai-langchain-autogen-demo. Мультиагентная система (SchemaAgent, ShipmentAgent, CRMAgent). Декомпозиция на агентов с разными зонами ответственности.

### C. AI-ассистенты для промышленного обслуживания (ключевые!)

**[7] giorgosfatouros/llm-chat-engine.** https://github.com/giorgosfatouros/llm-chat-engine. FastAPI + LangChain + GPT + Docker. **LLM-чатбот для Industrial 5.0 maintenance** — загрузка manuals, RAG-индексация, streaming. **Главный референс по теме**.

**[8] mr-Anil-prajapati/AI-Based-Industrial-Maintenance-Assistant.** https://github.com/mr-Anil-prajapati/AI-Based-Industrial-Maintenance-Assistant. FastAPI + RAG + локальный DeepSeek-R1 GGUF + PySide6. Read-only безопасное офлайн-решение для промдиагностики.

**[9] LGDiMaggio/predictive-maintenance-mcp.** https://github.com/LGDiMaggio/predictive-maintenance-mcp. Python + MCP + Claude API + ISO 13374 + ISO 20816-3. **52 MCP-эндпоинта для вибродиагностики**, генерация HTML/Word отчётов. Образец описания tool-схем для Claude.

**[10] mongodb-industry-solutions/Leafy-Predictive-Maintenance-Agents.** https://github.com/mongodb-industry-solutions/Leafy-Predictive-Maintenance-Agents. LangChain + Cohere + Atlas Vector Search. Predictive Maintenance Agent + Process Optimization Agent.

### D. Boilerplate / шаблоны (старт проекта)

**[11] fastapi/full-stack-fastapi-template** 30k+★. https://github.com/fastapi/full-stack-fastapi-template. FastAPI + SQLModel + PostgreSQL + **React + TypeScript + Vite + Tailwind + shadcn/ui** + Docker Compose + JWT. **Точное совпадение со стеком**! Идеальная стартовая основа.

**[12] vstorm-co/full-stack-ai-agent-template.** https://github.com/vstorm-co/full-stack-ai-agent-template. FastAPI + Next.js 15 + 6 фреймворков агентов (PydanticAI, LangChain, LangGraph, CrewAI) + 4 vector store (включая pgvector) + WebSocket-стриминг.

**[13] langchain-ai/agent-chat-ui** (официальный). https://github.com/langchain-ai/agent-chat-ui. React + LangGraph готовый фронтенд для общения с любым LangGraph-агентом.

**[14] langchain-ai/react-agent.** https://github.com/langchain-ai/react-agent. LangGraph + ReAct-pattern + langchain-anthropic (**Claude!**). Канонический ReAct-агент — основа для агента ТО.

### E. Claude API tool use

**[15] anthropics/claude-cookbooks** 13k+★ (официальный). https://github.com/anthropics/claude-cookbooks. Ключевые ноутбуки: `tool_use/customer_service_agent.ipynb`, `tool_use/calculator_tool.ipynb`, `tool_use/memory_cookbook.ipynb`, `patterns/agents/`, `misc/how_to_make_sql_queries.ipynb`. **Главный официальный источник примеров кода Claude tool use**.

**[16] umbertogriffo/rag-chatbot** ~600★. https://github.com/umbertogriffo/rag-chatbot. FastAPI + Vite/React/TypeScript + llama-cpp-python + Chroma. RAG для Markdown-документации с rewrite-retrieve-read.

**Стратегия сборки**: начать с `full-stack-fastapi-template` (стек React+Tailwind+FastAPI+PostgreSQL), наложить RAG из `danny-avila/rag_api` + ReAct-агент из `langchain-ai/react-agent` с Claude через `langchain-anthropic`.

---

## 4. Нормативная и методическая база

### А. ГОСТы для корпуса RAG

**[1] ГОСТ 20911-89 «Техническая диагностика. Термины и определения».** https://docs.cntd.ru/document/1200009481 (альт.: https://allgosts.ru/01/040/gost_20911-89). Базовая терминология: техническое состояние, диагностирование, контроль, диагностический параметр, прогнозирование. **Обязательный документ для глоссария — индексировать первым**.

**[2] ГОСТ 18322-2016 «Система технического обслуживания и ремонта техники. Термины и определения».** https://docs.cntd.ru/document/1200144954. Виды и методы ТО и ремонтов, показатели системы ТОиР. Ключевой нормативный источник по типам ТО.

**[3] ГОСТ Р 53564-2009 «Контроль состояния и диагностика машин. Мониторинг состояния оборудования опасных производств».** https://docs.cntd.ru/document/1200076745 (альт.: http://vsegost.com/Catalog/48/48744.shtml). Классификация и требования к системам мониторинга. **Обязателен** для главы «Анализ предметной области».

**[4] ГОСТ Р ИСО 13381-1-2016 «Контроль состояния и диагностика машин. Прогнозирование технического состояния. Часть 1».** https://docs.cntd.ru/document/1200142489 (PDF: https://meganorm.ru/Data/639/63904.pdf). Базис для модуля прогнозирования в LLM-агенте.

**[5] ГОСТ Р 27.606-2013 «Управление надёжностью. Техническое обслуживание, ориентированное на безотказность» (RCM).** https://docs.cntd.ru/document/1200104775. Методология RCM — ключевой стандарт для алгоритмов рекомендаций.

**[6] ГОСТ Р 71853-2024 «Единая энергетическая система... Система удалённого мониторинга и диагностики оборудования объектов электроэнергетики. Общие требования».** Введён 01.01.2025. Карточка: https://docs.cntd.ru/document/1310017753. Справка: https://rzia.ru/post170135.html. ⚠ **Уточнение**: в задаче назван «СУМиД» (управления), но официальное название — «удалённого мониторинга и диагностики». **Свежайший профильный стандарт — критически важен**.

**[7] ГОСТ Р 58651.1-2019 «Информационная модель электроэнергетики. Основные положения» (CIM).** https://docs.cntd.ru/document/1200169329. Модель данных для схемы PostgreSQL.

**[8] Серия ГОСТ Р МЭК 61850 «Сети и системы связи на подстанциях»**:
- Часть 1 (введение): https://docs.cntd.ru/document/1200091383
- Часть 3: https://docs.cntd.ru/document/1200044032
- Часть 6 (язык SCL): https://docs.cntd.ru/document/1200081013
- Часть 7-1 (структура): https://docs.cntd.ru/document/gost-r-mek-61850-7-1-2009
- Часть 7-3 (классы данных): https://docs.cntd.ru/document/1200083436
- Часть 7-4 (логические узлы): https://docs.cntd.ru/document/1200095441

**[9] РД 34.45-51.300-97 «Объём и нормы испытаний электрооборудования»** (правопреемник упомянутого в ТЗ РД 34.46.303-98). https://www.rosteplo.ru/Npb_files/npb_shablon.php?id=2082. Актуальная редакция: **СТО 34.01-23.1-001-2017** — https://ik-gefest.ru/document/СТО%2034.01-23.1-001-2017.pdf. **Главный нормативный документ корпуса RAG** — содержит типовые операции ТО для всех видов ВВ-оборудования.

⚠ **Уточнение**: указанный в ТЗ «РД 34.46.303-98» относится к котельным установкам (РД 153-34.1-26.303-98), а не к электрооборудованию. Согласовать с научным руководителем — корректное обозначение РД 34.45-51.300-97 / СТО 34.01-23.1-001-2017.

**[10] ПТЭЭП — Правила технической эксплуатации электроустановок потребителей**, гл. 3.6: https://www.elec.ru/library/direction/pteep/glava-3-6.html. Приложение 1 (нормы испытаний): http://www.eleco.ru/lib1/docs/rules/rules3/rules3-pril1.html.

### Б. Открытые учебные пособия по диагностике ВВ-оборудования

**[11] Хальясмаа А.И., Дмитриев С.А., Кокин С.Е., Глушков Д.А. «Диагностика электрооборудования электрических станций и подстанций»** (УрФУ, 2015, 64 с.). PDF: https://elar.urfu.ru/bitstream/10995/34803/1/978-5-7996-1493-5.pdf. Методы диагностики, нормативная база, ИК-диагностика, методы для трансформаторов, выключателей, кабельных линий. **Ключевое русскоязычное учебное пособие** — основа корпуса RAG.

**[12] АмГУ. «Методы диагностики электрооборудования электроустановок»** (для аспирантов 13.06.01). PDF: https://irbis.amursu.ru/DigitalLibrary/AmurSU_Edition/10691.pdf. Вибро-, тепловая, газо-хроматографическая диагностика.

**[13] Полищук В.И. «Эксплуатация, диагностика и ремонт электрооборудования»** (М.: ИНФРА-М, 2024). https://znanium.ru/catalog/document?id=438865. Современный учебник 2024 г. с разделом «Цифровая диагностика».

**[14] Коломиец Н.В. и др. «Электрическая часть электростанций и подстанций»** (ТПУ). https://portal.tpu.ru/SHARED/k/KRIVOVA_LV/Uchebnaya/Tab/tutorial.pdf

**[15] ТПУ «Эксплуатация электрооборудования электрических станций»** (2024). https://portal.tpu.ru/SHARED/d/DIMMASSIKK/academics/Эксплуат.ЭО%20ЭС/ЛК%201.pdf. Конспект лекций по эксплуатации генераторов, трансформаторов, РУ, релейной защиты.

**[16] СПбПУ «Электрическая часть систем электроснабжения станций и подстанций».** https://elib.spbstu.ru/dl/2/si20-171.pdf/info

### Приоритетная выборка для индексации в pgvector

**Ядро корпуса**: ГОСТ 20911-89, ГОСТ 18322-2016, РД 34.45-51.300-97 / СТО 34.01-23.1-001-2017, ГОСТ Р 71853-2024, ГОСТ Р ИСО 13381-1-2016, ГОСТ Р 27.606-2013, учебник Хальясмаа (УрФУ), ПТЭЭП гл. 3.6.

**Контекстный слой**: серия ГОСТ Р МЭК 61850 (части 1, 7-1, 7-4), ГОСТ Р 58651.1-2019, учебники ТПУ/СПбПУ.

---

## 5. Учебные материалы по стеку

### Официальная документация

**[1] LangChain — RAG agent tutorial.** https://docs.langchain.com/oss/python/langchain/rag (документация, средний уровень). Канонический туториал по RAG-агенту.

**[2] LangChain — Build a SQL agent.** https://docs.langchain.com/oss/python/langchain/sql-agent. SQLDatabaseToolkit (sql_db_query, sql_db_schema, sql_db_list_tables) — прямо применимо к таблицам ТО.

**[3] Anthropic — Tool use overview.** https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview. Client tools vs server tools, агентный loop.

**[4] Anthropic — How tool use works.** https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works. stop_reason="tool_use", цикл tool_use → tool_result.

**[5] Anthropic — How to implement tool use.** https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use. Tool runner SDK, обработка ошибок.

**[6] Anthropic Engineering — Advanced tool use.** https://www.anthropic.com/engineering/advanced-tool-use. Tool Search Tool, Programmatic Tool Calling. **Must-read для архитектуры агента**.

**[7] FastAPI — официальная документация (русская версия).** https://fastapi.tiangolo.com/ru/. Раздел Tutorial - User Guide.

**[8] pgvector — README.** https://github.com/pgvector/pgvector. Установка, типы индексов IVFFlat/HNSW, операторы расстояния.

### Англоязычные туториалы

**[9] Vitalii Honchar. Python RAG API Tutorial with LangChain & FastAPI.** https://www.vitaliihonchar.com/insights/python-rag-api (статья, средний). Подробное руководство с DocumentService, ChatService, pgvector.

**[10] Silversky. Building a Conversational SQL Agent with LangChain and FastAPI.** https://medium.com/@silverskytechnology/building-a-conversational-sql-agent-with-langchain-and-fastapi-7fb2c96228a5

**[11] Suboor Khan. Claude API Masterclass: Tool Use, Vision & Extended Thinking.** https://www.suboorkhan.com/blogs/claude-api-masterclass-tool-use-vision

### Русскоязычные материалы (Habr и др.)

**[12] Habr. Собираем AI-агента нового поколения: Python, RAG и MCP.** https://habr.com/ru/articles/1025428/ (средний). LangGraph + LangChain-Anthropic (**Claude!**) + RAG по PDF — полный код.

**[13] Habr. От LangChain к LangGraph: детально разбираемся с фреймворками.** https://habr.com/ru/articles/956940/

**[14] Habr. LangChain для бывалых: память и агенты.** https://habr.com/ru/articles/733262/

**[15] Habr. Создаём свой RAG: введение в LangGraph.** https://habr.com/ru/articles/907844/. ToolNode, function calling в RAG.

**[16] Habr. Создание умных AI-агентов: полный курс по LangGraph (часть 2).** https://habr.com/ru/companies/amvera/articles/948000/. ChatAnthropic, контекст, диалоговые агенты.

**[17] Habr. LangChain vs LlamaIndex: проектируем RAG.** https://habr.com/ru/companies/raft/articles/875758/

**[18] Habr. Как сделать RAG для своей компании.** https://habr.com/ru/articles/905076/. MCP-роутер, FastAPI, LangChain, JIRA-tool — практический образец.

**[19] Habr. Векторный поиск в PostgreSQL: PGVector, SQLAlchemy и FastAPI.** https://habr.com/ru/articles/1006364/. **Точно по стеку**: pgvector в Docker, alembic, asyncpg.

**[20] Habr (Selectel). Векторный поиск внутри PostgreSQL: pgvector.** https://habr.com/ru/companies/selectel/articles/920824/

**[21] Habr. Выбираем векторную БД для AI-агентов и RAG.** https://habr.com/ru/articles/961088/. Обзор Milvus, Qdrant, Weaviate, Chroma, pgvector — для обоснования выбора.

**[22] Habr. FastAPI: гайд по нормальной структуре.** https://habr.com/ru/articles/970798/

**[23] Habr. Генерация дополненного извлечения (RAG): от теории к LangChain.** https://habr.com/ru/articles/862870/

### Курсы (Stepik / онлайн-платформы)

**[24] Stepik. LangChain: с нуля до продакшн LLM-приложений.** https://stepik.org/course/250355/promo. RAG по PDF с цитатами, многошаговый агент, веб-приложение.

**[25] Stepik. LangChain/LangGraph — Создание AI-агентов на Python + RAG + MCP.** https://stepik.org/course/241341/promo. ReAct, LangGraph Studio.

**[26] Stepik. Создание AI-ассистентов для ИТ-инфраструктуры (LLM, RAG, agents).** https://stepik.org/course/248396/promo. **Методически очень близко к курсовой**.

**[27] AI Talent Hub (ИТМО). LLM-курс.** https://ai.itmo.ru/llm и https://llmcourse.tech. PyTorch, HuggingFace, vLLM, RAG, агенты.

### Видеоматериалы

**[28] YouTube. AI Talent Hub (канал).** https://www.youtube.com/@aitalenthub. Воркшопы по LLM, RAG, агентам.

**[29] YouTube. Воркшоп: Базовый RAG: создай свой поисковик на LLM.** https://www.youtube.com/watch?v=bfsL5nLOYbU (Дарья Андреева, X5 Tech).

**[30] YouTube. AI engineering 2026: LLM, RAG, AI агенты.** https://www.youtube.com/watch?v=7toDgSozmEs

---

## 6. Анализ аналогов

### Ближайшие коммерческие и open-source системы

**1. IBM Maximo Application Suite (MAS) 9.1 + Maximo Condition Insight** (IBM, США). https://www.ibm.com/products/maximo. Унифицированный пакет EAM/APM с генеративным AI на базе watsonx.ai (IBM Granite). Версия 9.1 (июнь 2025) добавила Condition Insight — отвечает на вопросы вроде «какие наряды без планов работ?» на естественном языке, выдаёт прескриптивные рекомендации. **Отличия от проекта**: закрытая лицензия от десятков тысяч $/год; универсален vs специализация студента под высоковольтное; недоступен в РФ; зависимость от Watson и OpenShift.

**2. Siemens Senseye Predictive Maintenance + Maintenance Copilot** (Siemens, Германия). https://www.siemens.com/us/en/products/services/digital-enterprise-services/analytics-artificial-intelligence-services/predictive-services/senseye-predictive-maintenance/platform-overview.html. Облачная AI-платформа PdM, с 2024 — Maintenance Copilot (ML+LLM, мультиязычный, case-based reasoning). **Отличия**: ориентирован на массовое промоборудование (прессы, конвейеры), не на ВВ; требует IoT-датчиков, проект студента работает с документацией и журналами; недоступен в РФ.

**3. GE Vernova Asset Performance Management + SmartSignal** (GE Vernova, США). https://www.gevernova.com/software/products/asset-performance-management. >320 готовых Digital Twin шаблонов, мониторинг ~1000 электростанций. Лидер по Verdantix Green Quadrant 2024. **Отличия**: фокус на IoT-телеметрии vs RAG-документации у студента; миллионы $ внедрения.

**4. Hitachi Energy Lumada APM** (Hitachi Energy, Швейцария/Япония). https://www.hitachienergy.com/products-and-solutions/asset-and-work-management/lumada-apm. ⭐ **Самый близкий по предметной области аналог**: специализация на ВВ-оборудовании (трансформаторы 420 кВ, выключатели, разъединители), интеграция с IEC 61850. Используется датским Energinet и Inner Mongolia Power. **Отличия**: закрыт для РФ; работает на телеметрии, проект студента — на документации и LLM-рассуждении.

**5. ABB Ability Genix APM + Genix APM Copilot** (ABB, Швейцария). https://new.abb.com/process-automation/genix/genix-apm. LLM на Microsoft Azure OpenAI Services (GPT-4) для предиктивного обслуживания. Сильная позиция в ВВ-оборудовании (собственная продукция ABB). **Отличия**: Azure OpenAI недоступен в РФ; огромная Industrial Suite-инфраструктура vs минимальный стек студента.

**6. GigaChat Enterprise (Сбер, Россия)**. https://developers.sber.ru/portal/products/gigachat-api. Корпоративная платформа AI-агентов; флагман GigaChat Ultra; работа с базами знаний, файлами до 5 ГБ. 42% промкомпаний РФ используют GenAI. **Отличия**: универсальная платформа vs конкретная DSS у студента; проект — учебная open-source реализация. **Можно отметить как путь импортозамещения**: архитектура студента переключаема с Claude на GigaChat.

**7. YandexGPT 5 Pro / 5.1 Pro (Yandex Cloud, Россия)**. https://yandex.cloud/ru/services/yandexgpt. Лаборатория JET & YandexGPT (с «Инфосистемы Джет») тестирует LLM в промышленности. Цены 0,20–0,80 ₽/1K токенов. **Отличия**: API/модель vs готовая система ТО у студента.

**8. Цифрум АтомМайнд (ГК Росатом, Россия)**. https://www.rosatom.ru/production/supercomputer-and-software/tsifrovye-produkty/. Платформа цифровизации с предиктивной аналитикой. С 2025 г. развивает GenAI совместно с НИЯУ МИФИ. **Отличия**: внутренний продукт Росатома, классический ML на телеметрии; проект студента — LLM-агент на знаниях/документах.

**9. PrivateGPT (Zylon, open-source, Apache 2.0)**. https://github.com/zylon-ai/private-gpt. ⭐ **Стек практически идентичен**: FastAPI + Python + LlamaIndex + векторная БД. **Отличия**: общий фреймворк vs специализированная DSS у студента; PrivateGPT — «движок», проект — приложение поверх (бизнес-логика, роли инженера/диспетчера). **Обязательно показать в курсовой как самый близкий технологический референс**.

**10. Verba: The Golden RAGtriever (Weaviate, open-source BSD-3)**. https://github.com/weaviate/Verba. ⭐ **Стек идентичен**: FastAPI + React + Anthropic Claude + векторная БД. **Отличия**: нет агентских функций (tool calling, multi-step reasoning) — у студента есть LangChain-агенты; pgvector проще чем Weaviate; отсутствует предметная онтология ТО. **Почти идентичный технологический референс — обязателен в курсовой**.

### Сравнительная таблица аналогов

| Система | Лицензия | LLM | Доступность в РФ | Цена |
|---|---|---|---|---|
| IBM Maximo App Suite 9.1 | Проприетарная | watsonx.ai (Granite) | Нет (санкции) | От ~$164/user/мес AppPoints |
| Siemens Senseye PdM | Проприетарная (SaaS) | ML + GenAI | Нет | По запросу |
| GE Vernova APM / SmartSignal | Проприетарная | GenAI пилоты | Нет | От сотен тыс. $ |
| Hitachi Energy Lumada APM | Проприетарная | ML, базовый AI | Нет | По запросу |
| ABB Ability Genix APM Copilot | Проприетарная | Azure OpenAI / GPT-4 | Нет | По запросу |
| GigaChat Enterprise (Сбер) | Проприетарная (РФ) | GigaChat Ultra | **Да** | По договору |
| YandexGPT 5 Pro | Проприетарная (РФ) | YandexGPT | **Да** | 0,20–0,80 ₽/1K токенов |
| Цифрум АтомМайнд | Проприетарная (внутр.) | ML | **Да** | Внутренний |
| **PrivateGPT (Zylon)** | **Open-source** | Любые | Гибко | **Бесплатно** |
| **Verba (Weaviate)** | **Open-source** | Claude/OpenAI/Ollama | Гибко | **Бесплатно** |
| **🎓 Проект студента** | **Open-source (учебный)** | **Claude API (опц. GigaChat)** | **Да (ГОСТы РФ)** | **Бесплатно** |

### Ключевые выводы для курсовой

**Уникальность проекта в матрице конкурентов**: (1) узкая специализация на ВВ-оборудовании как у Hitachi Lumada, но open-source; (2) российская нормативная база (ГОСТ, ПТЭЭП, РД), тогда как западные ориентированы на IEEE/IEC, а GigaChat/YandexGPT — универсальные модели без готовой DSS; (3) современный LLM-агентский стек (LangChain + Claude + pgvector); (4) доступность — все enterprise-аналоги недоступны или дороги в 2026 для среднего российского предприятия из-за санкций; (5) простота развёртывания — FastAPI/PostgreSQL не требуют Kubernetes/OpenShift.

---

## 7. Структура курсовой и список литературы

### Типовая структура курсовой работы (для УУНиТ, ИСиТ, 4 семестр)

**Введение** (3-5 стр.): актуальность, цель, задачи, объект, предмет, методы, практическая значимость, структура работы.

**Глава 1. Теоретические основы и анализ предметной области** (15-20 стр.):
1.1. Особенности технического обслуживания высоковольтного электрооборудования (виды ТО, нормативная база, ПТЭЭП, ГОСТ 18322-2016, ГОСТ Р 53564, РД 34.45-51.300-97).
1.2. Информационные системы поддержки принятия решений: классификация, архитектура.
1.3. Большие языковые модели (LLM) и парадигма RAG: принципы, архитектура, ограничения.
1.4. Агентский подход и tool use: ReAct, function calling, фреймворки (LangChain, LangGraph).
1.5. Векторные базы данных и pgvector: алгоритмы (HNSW, IVFFlat).
1.6. Анализ существующих аналогов (IBM Maximo, Hitachi Lumada, PrivateGPT, Verba, GigaChat) и обоснование разработки.

**Глава 2. Проектирование интеллектуальной ИСППР** (15-20 стр.):
2.1. Постановка задачи и функциональные требования.
2.2. Архитектура системы (диаграмма компонентов): backend (FastAPI), LLM-агент (LangChain + Claude), модуль RAG (pgvector), frontend (React + Tailwind).
2.3. Проектирование БД оборудования (ER-диаграмма, схема PostgreSQL с учётом CIM по ГОСТ Р 58651).
2.4. Проектирование инструментов (tools) агента: query_equipment_db, search_documentation, get_maintenance_schedule, log_inspection_result.
2.5. Проектирование RAG-конвейера: chunking стратегия для ГОСТов и РД, embedding-модель, индексация в pgvector.
2.6. Use-case диаграммы и сценарии взаимодействия инженера с системой.

**Глава 3. Реализация и тестирование** (15-20 стр.):
3.1. Программная реализация backend на FastAPI (структура проекта, эндпоинты, асинхронность).
3.2. Реализация LLM-агента: системный промпт, схемы tool use для Claude API, обработка цикла tool_use → tool_result.
3.3. Реализация RAG: загрузка корпуса (ГОСТы, РД, учебники), чанкинг, эмбеддинги, поиск по pgvector с HNSW-индексом.
3.4. Реализация frontend на React + Tailwind: чат-интерфейс, отображение источников цитирования.
3.5. Тестирование: метрики качества RAG (precision@k, recall@k, MRR), оценка ответов агента, сценарные тесты.
3.6. Демонстрация работы на типовых сценариях ТО.

**Заключение** (2-3 стр.): итоги, достигнутые результаты, направления развития (импортозамещение через GigaChat, мультимодальность, интеграция с SCADA по МЭК 61850).

**Список литературы** (15-25 источников).

**Приложения**: листинги кода, диаграммы, скриншоты UI, выгрузки тестов.

### Пример формулировок (введение)

**Цель работы**: разработка интеллектуальной информационной системы поддержки принятия решений для специалистов по техническому обслуживанию высоковольтного электрооборудования на основе LLM-агента с инструментами доступа к базе данных оборудования и системе семантического поиска по технической документации.

**Задачи**:
1. Проанализировать предметную область ТО ВВ-оборудования и нормативную базу (ГОСТы, РД, ПТЭЭП).
2. Исследовать современные подходы к построению LLM-агентов и RAG-систем; выполнить сравнительный анализ аналогов.
3. Спроектировать архитектуру ИСППР с использованием FastAPI, LangChain, PostgreSQL/pgvector и Claude API.
4. Разработать модель данных оборудования и сформировать корпус технической документации для RAG.
5. Реализовать программный прототип системы (backend + frontend + LLM-агент с tools).
6. Провести тестирование качества RAG-поиска и ответов агента, оценить эффективность системы.

**Объект исследования**: процесс информационной поддержки принятия решений при техническом обслуживании высоковольтного электрооборудования.

**Предмет исследования**: методы и средства построения интеллектуальной ИСППР на основе LLM-агента с инструментами и поисковой подсистемой Retrieval-Augmented Generation.

**Методы исследования**: системный анализ, объектно-ориентированное проектирование (UML), методы NLP и машинного обучения (трансформерные LLM, dense retrieval, ANN-поиск), методы программной инженерии (API-first, DDD).

### Рекомендации по теоретической части

В **главе 1** сделать акцент на следующих понятиях с обязательными определениями: «интеллектуальная информационная система поддержки принятия решений (ИСППР)», «техническое диагностирование» (по ГОСТ 20911-89), «техническое обслуживание» (по ГОСТ 18322-2016), «большая языковая модель», «Retrieval-Augmented Generation (RAG)», «агент LLM», «инструмент (tool) / function calling», «векторная база данных», «эмбеддинг», «семантический поиск (HNSW, IVFFlat)». Привести классификацию RAG (Naive / Advanced / Modular по Gao 2023), парадигму ReAct (Yao 2022), сравнение фреймворков (LangChain vs LangGraph vs LlamaIndex). Обосновать выбор Claude API (точность tool use по Berkeley Function Calling Leaderboard, окно контекста 200К) и pgvector (отсутствие необходимости в отдельной инфраструктуре, ACID-гарантии).

### Список литературы (оформление по ГОСТ Р 7.0.5-2008)

**Российские нормативные документы**:

1. ГОСТ 20911-89. Техническая диагностика. Термины и определения. – Введ. 1991-01-01. – М.: Стандартинформ, 2009. – 11 с. – URL: https://docs.cntd.ru/document/1200009481 (дата обращения: 28.04.2026).
2. ГОСТ 18322-2016. Система технического обслуживания и ремонта техники. Термины и определения. – Введ. 2017-09-01. – М.: Стандартинформ, 2017. – URL: https://docs.cntd.ru/document/1200144954 (дата обращения: 28.04.2026).
3. ГОСТ Р 53564-2009. Контроль состояния и диагностика машин. Мониторинг состояния оборудования опасных производств. Требования к системам мониторинга. – М.: Стандартинформ, 2010. – URL: https://docs.cntd.ru/document/1200076745 (дата обращения: 28.04.2026).
4. ГОСТ Р ИСО 13381-1-2016. Контроль состояния и диагностика машин. Прогнозирование технического состояния. Часть 1. Общее руководство. – М.: Стандартинформ, 2016. – URL: https://docs.cntd.ru/document/1200142489 (дата обращения: 28.04.2026).
5. ГОСТ Р 27.606-2013. Надёжность в технике. Управление надёжностью. Техническое обслуживание, ориентированное на безотказность. – М.: Стандартинформ, 2014. – URL: https://docs.cntd.ru/document/1200104775 (дата обращения: 28.04.2026).
6. ГОСТ Р 71853-2024. Единая энергетическая система и изолированно работающие энергосистемы. Система удалённого мониторинга и диагностики оборудования объектов электроэнергетики. Общие требования. – Введ. 2025-01-01. – М.: Российский институт стандартизации, 2024. – URL: https://docs.cntd.ru/document/1310017753 (дата обращения: 28.04.2026).
7. ГОСТ Р 58651.1-2019. Информационная модель электроэнергетики. Основные положения. – М.: Стандартинформ, 2019. – URL: https://docs.cntd.ru/document/1200169329 (дата обращения: 28.04.2026).
8. СТО 34.01-23.1-001-2017. Объём и нормы испытаний электрооборудования. – М.: ПАО «Россети», 2017. – URL: https://ik-gefest.ru/document/СТО%2034.01-23.1-001-2017.pdf (дата обращения: 28.04.2026).

**Российские монографии и учебные пособия**:

9. Хальясмаа А. И., Дмитриев С. А., Кокин С. Е., Глушков Д. А. Диагностика электрооборудования электрических станций и подстанций : учебное пособие. – Екатеринбург : Изд-во Урал. ун-та, 2015. – 64 с. – URL: https://elar.urfu.ru/bitstream/10995/34803/1/978-5-7996-1493-5.pdf (дата обращения: 28.04.2026).
10. Полищук В. И. Эксплуатация, диагностика и ремонт электрооборудования : учебное пособие. – М. : ИНФРА-М, 2024. – URL: https://znanium.ru/catalog/document?id=438865 (дата обращения: 28.04.2026).
11. Бородулин И. В. Технология RAG (Retrieval-Augmented Generation) как инновационный подход в LLM // КиберЛенинка. – 2024. – URL: https://cyberleninka.ru/article/n/tehnologiya-rag-retrieval-augmented-generation-kak-innovatsionnyy-podhod-v-llm (дата обращения: 28.04.2026).
12. Архитектура системы предсказательного технического обслуживания сложных многообъектных систем в концепции Индустрии 4.0 // КиберЛенинка. – URL: https://cyberleninka.ru/article/n/arhitektura-sistemy-predskazatelnogo-tehnicheskogo-obsluzhivaniya-slozhnyh-mnogoobektnyh-sistem-v-kontseptsii-industrii-4-0 (дата обращения: 28.04.2026).
13. Современные решения диагностики и мониторинга высоковольтного оборудования // КиберЛенинка. – URL: https://cyberleninka.ru/article/n/sovremennye-resheniya-diagnostiki-i-monitoringa-vysokovoltnogo-oborudovaniya (дата обращения: 28.04.2026).

**Зарубежные академические статьи**:

14. Lewis P., Perez E., Piktus A. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks // Advances in Neural Information Processing Systems (NeurIPS). – 2020. – arXiv:2005.11401. – URL: https://arxiv.org/abs/2005.11401.
15. Yao S., Zhao J., Yu D. et al. ReAct: Synergizing Reasoning and Acting in Language Models // Proc. Intl. Conf. on Learning Representations (ICLR). – 2023. – arXiv:2210.03629. – URL: https://arxiv.org/abs/2210.03629.
16. Schick T., Dwivedi-Yu J., Dessì R. et al. Toolformer: Language Models Can Teach Themselves to Use Tools // NeurIPS. – 2023. – arXiv:2302.04761. – URL: https://arxiv.org/abs/2302.04761.
17. Gao Y., Xiong Y., Gao X. et al. Retrieval-Augmented Generation for Large Language Models: A Survey. – 2023. – arXiv:2312.10997. – URL: https://arxiv.org/abs/2312.10997.
18. Tao L., Huang Q., Wu X. et al. LLM-R: A Framework for Domain-Adaptive Maintenance Scheme Generation Combining Hierarchical Agents and RAG. – 2024. – arXiv:2411.04476. – URL: https://arxiv.org/abs/2411.04476.
19. Harbola C., Purwar A. PARAM: Prescriptive Agents based on RAG for Automated Maintenance. – 2025. – arXiv:2508.04714. – URL: https://arxiv.org/abs/2508.04714.
20. Alawadhi S., Abbas N. Optimizing Retrieval-Augmented Generation for Electrical Engineering: A Case Study on ABB Circuit Breakers. – 2025. – arXiv:2505.17520. – URL: https://arxiv.org/abs/2505.17520.
21. Jing L., Rahman A. Fault Diagnosis in Power Grids with Large Language Model. – 2024. – arXiv:2407.08836. – URL: https://arxiv.org/abs/2407.08836.
22. Masterman T., Besen S., Sawtell M., Chao A. The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey. – 2024. – arXiv:2404.11584. – URL: https://arxiv.org/abs/2404.11584.
23. Hybrid AI and LLM-Enabled Agent-Based Real-Time Decision Support Architecture for Industrial Batch Processes // AI (MDPI). – 2026. – Vol. 7, No. 2. – Art. 51. – DOI: 10.3390/ai7020051. – URL: https://www.mdpi.com/2673-2688/7/2/51.
24. Enhancing Security and Applicability of Local LLM-Based Document Retrieval Systems in Smart Grid Isolated Environments // Electronics (MDPI). – 2025. – Vol. 14, No. 17. – Art. 3407. – DOI: 10.3390/electronics14173407. – URL: https://www.mdpi.com/2079-9292/14/17/3407.

**Документация и учебные материалы по стеку**:

25. LangChain Documentation : RAG Agent Tutorial / LangChain AI. – URL: https://docs.langchain.com/oss/python/langchain/rag (дата обращения: 28.04.2026).
26. Anthropic Tool Use Documentation / Anthropic. – URL: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview (дата обращения: 28.04.2026).
27. FastAPI : Документация / Sebastián Ramírez. – URL: https://fastapi.tiangolo.com/ru/ (дата обращения: 28.04.2026).
28. pgvector : Open-source vector similarity search for Postgres / A. Kane. – URL: https://github.com/pgvector/pgvector (дата обращения: 28.04.2026).

---

## Финальные рекомендации

Сначала **разверните стартовый шаблон** `fastapi/full-stack-fastapi-template`, добавьте на него RAG-сервис из `danny-avila/rag_api` и ReAct-агента из `langchain-ai/react-agent` с интеграцией Claude через `langchain-anthropic`. Корпус документов RAG соберите из приоритетного ядра ГОСТов (20911, 18322, ГОСТ Р 71853-2024, ИСО 13381-1, 27.606), РД 34.45-51.300-97 и учебника Хальясмаа (УрФУ). В качестве методологической базы цитируйте Lewis 2020 (RAG), Yao 2022 (ReAct), Tao 2024 (LLM-R) и Alawadhi 2025 (RAG для ABB Circuit Breakers — ближайшая по предмету). В разделе аналогов противопоставьте проект коммерческим закрытым системам (IBM Maximo, Hitachi Lumada, Siemens Senseye), отметив доступность open-source стека и адаптацию под российскую нормативную базу.

⚠ **Уточнить с научным руководителем два момента в постановке задачи**: (1) аббревиатура «СУМиД» в ГОСТ Р 71853-2024 — официальное название «удалённого мониторинга и диагностики», а не «управления»; (2) указанный РД 34.46.303-98 не существует в предметной области электрооборудования — корректное обозначение РД 34.45-51.300-97 / СТО 34.01-23.1-001-2017.