import streamlit as st

_STEP_ICON = {
    "thought": "💭 Размышление",
    "action": "🔧 Действие",
    "observation": "📄 Наблюдение",
    "final": "✅ Итог",
}


def render_sources(citations: list[dict]) -> None:
    if not citations:
        return
    with st.expander(f"Источники ({len(citations)})", expanded=False):
        for c in citations:
            score_pct = max(0, int(min(c.get("score", 0), 1) * 100))
            st.markdown(
                f"**{c['source']}** — с. {c['page']} *(релевантность: {score_pct}%)*"
            )
            st.text(c.get("excerpt", ""))
            st.divider()


def render_trace(trace: list[dict], tools_used: list[str], iterations: int) -> None:
    if not trace:
        return
    used = ", ".join(tools_used) if tools_used else "—"
    with st.expander(f"Ход рассуждения (ReAct) · шагов: {iterations} · инструменты: {used}", expanded=False):
        for step in trace:
            label = _STEP_ICON.get(step["type"], step["type"])
            if step["type"] == "action":
                st.markdown(f"**{label}:** `{step['tool_name']}`")
                st.code(step.get("tool_input", ""), language="text")
            else:
                st.markdown(f"**{label}:**")
                st.text(step.get("content", ""))
            st.divider()


def render_message(role: str, content: str, citations: list[dict] | None = None) -> None:
    with st.chat_message(role):
        st.markdown(content)
        if citations:
            render_sources(citations)
