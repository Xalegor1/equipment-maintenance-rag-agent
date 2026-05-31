import streamlit as st

from frontend.utils import ingest_pdf


def render_sidebar() -> str:
    """Сайдбар: выбор режима + загрузка документа. Возвращает выбранный режим."""
    st.sidebar.title("ИСППР · ТО оборудования")
    st.sidebar.caption("LLM-агент + RAG по нормативной документации")

    st.sidebar.divider()
    st.sidebar.subheader("Режим работы")
    mode = st.sidebar.radio(
        "Режим",
        options=["Агент (LLM + RAG + БД)", "Чистый RAG"],
        label_visibility="collapsed",
        help=(
            "Агент сам планирует шаги: запрашивает БД оборудования и ищет нормативы. "
            "Чистый RAG отвечает только по документации (для сравнения)."
        ),
    )

    st.sidebar.divider()
    st.sidebar.subheader("Загрузка документа")

    uploaded = st.sidebar.file_uploader(
        "Выберите PDF",
        type=["pdf"],
        help="Загрузите PDF (ГОСТ, РД, регламент) в базу знаний.",
    )

    if uploaded and st.sidebar.button("Загрузить в базу", use_container_width=True):
        with st.sidebar.status("Загрузка..."):
            try:
                result = ingest_pdf(uploaded.read(), uploaded.name)
                st.sidebar.success(
                    f"Загружено **{result['filename']}**\n"
                    f"- Фрагментов: {result['chunk_count']}\n"
                    f"- Размер индекса: {result['index_size']}\n"
                    f"- Время: {result['processing_ms']:.0f} мс"
                )
            except Exception as exc:
                st.sidebar.error(f"Ошибка загрузки: {exc}")

    return mode
