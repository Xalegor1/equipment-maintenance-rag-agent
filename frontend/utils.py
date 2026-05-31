import os

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 120.0  # секунд

_CONN_ERROR = "Не удаётся подключиться к API. Убедитесь, что бэкенд запущен."
_TIMEOUT_ERROR = "Превышено время ожидания ответа. Попробуйте ещё раз."


def _extract_error(exc: httpx.HTTPStatusError) -> str:
    try:
        detail = exc.response.json().get("detail", str(exc))
    except Exception:
        return exc.response.text or str(exc)
    if isinstance(detail, dict):
        return detail.get("message", str(detail))
    return str(detail)


def ingest_pdf(file_bytes: bytes, filename: str) -> dict:
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_URL}/api/v1/ingest",
                files={"file": (filename, file_bytes, "application/pdf")},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(_extract_error(exc)) from exc
            return response.json()
    except httpx.ConnectError:
        raise RuntimeError(_CONN_ERROR) from None
    except httpx.TimeoutException:
        raise RuntimeError(_TIMEOUT_ERROR) from None


def ask_question(question: str, top_k: int = 4) -> dict:
    """Чистый RAG: POST /api/v1/query."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_URL}/api/v1/query",
                json={"question": question, "top_k": top_k},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(_extract_error(exc)) from exc
            return response.json()
    except httpx.ConnectError:
        raise RuntimeError(_CONN_ERROR) from None
    except httpx.TimeoutException:
        raise RuntimeError(_TIMEOUT_ERROR) from None


def ask_agent(question: str) -> dict:
    """LLM-агент (RAG + база оборудования): POST /api/v1/agent."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_URL}/api/v1/agent",
                json={"question": question},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(_extract_error(exc)) from exc
            return response.json()
    except httpx.ConnectError:
        raise RuntimeError(_CONN_ERROR) from None
    except httpx.TimeoutException:
        raise RuntimeError(_TIMEOUT_ERROR) from None
