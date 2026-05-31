import streamlit as st

from frontend.components.chat import render_message, render_sources, render_trace
from frontend.utils import ask_agent, ask_question
from frontend.components.sidebar import render_sidebar

st.set_page_config(
    page_title="ИСППР · ТО оборудования",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """<style>
    h1 a, h2 a, h3 a { display: none !important; }
    </style>""",
    unsafe_allow_html=True,
)

mode = render_sidebar()
is_agent = mode.startswith("Агент")

st.title("ИСППР по техническому обслуживанию оборудования")
if is_agent:
    st.caption(
        "Режим: **LLM-агент**. Агент сам обращается к базе оборудования и нормативной "
        "документации, комбинируя данные в обоснованную рекомендацию."
    )
else:
    st.caption("Режим: **чистый RAG**. Ответ формируется только по найденной документации.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            render_sources(msg["citations"])
        if msg.get("trace"):
            render_trace(msg["trace"], msg.get("tools_used", []), msg.get("iterations", 0))

placeholder = (
    "Например: Трансформатор ТМ-630/10-2 давно не осматривался — что делать?"
    if is_agent
    else "Например: Какова периодичность осмотра масляного трансформатора?"
)

if prompt := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        spinner_text = "Агент рассуждает..." if is_agent else "Поиск по документации..."
        with st.spinner(spinner_text):
            try:
                if is_agent:
                    result = ask_agent(prompt)
                    answer = result["answer"]
                    st.markdown(answer)
                    st.caption(f"Время ответа: {result['latency_ms']:.0f} мс")
                    render_trace(result["trace"], result["tools_used"], result["iterations"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "trace": result["trace"],
                        "tools_used": result["tools_used"],
                        "iterations": result["iterations"],
                    })
                else:
                    result = ask_question(prompt)
                    answer = result["answer"]
                    citations = result["citations"]
                    st.markdown(answer)
                    st.caption(f"Время ответа: {result['latency_ms']:.0f} мс")
                    render_sources(citations)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                    })
            except Exception as exc:
                error_msg = str(exc) or "Произошла непредвиденная ошибка. Попробуйте ещё раз."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
