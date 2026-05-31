"""Сборка ReAct-агента на базе LangChain AgentExecutor."""
from __future__ import annotations

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from src.agent.prompt import REACT_PROMPT
from src.rag.config import Settings


def build_agent(tools: list[BaseTool], settings: Settings) -> AgentExecutor:
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        temperature=0,
        openai_api_key=settings.openai_api_key.get_secret_value(),
        max_retries=settings.openai_max_retries,
        request_timeout=30,
    )
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    # create_react_agent добавляет stop=["\nObservation"], чтобы модель не «дописывала»
    # наблюдения за инструменты (важно для надёжности gpt-4o-mini).
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=settings.agent_max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        verbose=False,
    )
