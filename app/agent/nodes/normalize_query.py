import re
import unicodedata
from typing import Any

from langchain_core.messages import HumanMessage

from app.agent.state import AgentState


def _basic_normalize(text: str) -> str:
    """
    Normalize user query for downstream software matching/search.

    What it does:
    - unicode normalization
    - lowercasing
    - replacing 'ё' -> 'е'
    - collapsing extra whitespace
    - removing most punctuation, but keeping useful symbols
      such as +, #, ., -, _
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = text.replace("ё", "е")

    # заменяет переносы и табуляцию пробелами
    text = re.sub(r"[\t\r\n]+", " ", text)

    # keep letters, digits, spaces and a few useful symbols
    text = re.sub(r"[^\w\s\+\#\.\-_]", " ", text, flags=re.UNICODE)

    # collapse duplicated spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_query(state: AgentState) -> dict[str, Any]:
    """
    LangGraph node:
    - extracts the latest user message from state['messages']
    - normalizes it
    - stores result in state['normalized_query']
    """
    messages = state.get("messages", [])

    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = getattr(msg, "content", "")
            if isinstance(content, str) and content.strip():
                last_user_message = content
                break

    if not last_user_message:
        return {
            "normalized_query": "",
            "error": "Could not extract user message for normalization.",
        }

    normalized = _basic_normalize(last_user_message)

    return {
        "normalized_query": normalized,
        "error": None,
    }