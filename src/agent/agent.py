"""Сборка агента на нативных вызовах функций OpenAI (tool-calling).

Tool-calling надёжнее текстового ReAct для gpt-4o-mini: нет хрупкого парсинга
формата Action/Observation, поэтому агент не зацикливается из-за «забытого»
префикса Final Answer. Трейс шагов по-прежнему доступен через intermediate_steps.
"""
from __future__ import annotations

from datetime import date

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from src.agent.prompt import SYSTEM_PROMPT
from src.rag.config import Settings


def build_agent(tools: list[BaseTool], settings: Settings) -> AgentExecutor:
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        temperature=0,
        openai_api_key=settings.openai_api_key.get_secret_value(),
        max_retries=settings.openai_max_retries,
        request_timeout=30,
    )
    system = SYSTEM_PROMPT.replace("__TODAY__", date.today().isoformat())
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=settings.agent_max_iterations,
        return_intermediate_steps=True,
        verbose=False,
    )
