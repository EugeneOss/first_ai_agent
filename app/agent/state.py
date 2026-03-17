from typing import Annotated, TypedDict, Optional, Any, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    # chatbot
    messages: Annotated[list[BaseMessage], add_messages]
    normalized_query: str

    #resolver
    intent_type: Literal["software_info", "allowed_software", "general_chat", None]
    matched_softwares: list[dict]
    resolved_software: dict | None
    clarification_needed: bool
    needs_web_search: bool
    web_queries: list[str]
   
    # web search
    search_results: dict[str, Any]

    # llm outputs
    summary: str
    html_result: str

    # error handling
    error: Optional[str | None]