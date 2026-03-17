from dotenv import load_dotenv

from app.agent.state import AgentState

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.nodes.chatbots import mid_chatbot
from app.agent.nodes.normalize_query import normalize_query
from app.agent.nodes.resolve_software import resolve_software_node
from app.agent.nodes.router import route_after_resolver
from app.agent.nodes.error import error_end
from app.agent.nodes.clarification import clarification
from app.agent.nodes.allowed_sofrware import listing_allowed_software
from app.agent.nodes.web_search import web_searcher_node
from app.agent.nodes.generate_html import html_generator_node

# Создаем graph
graph = StateGraph(AgentState)

# Создаем nodes
graph.add_node("chatbot", mid_chatbot)
graph.add_node("normalizer", normalize_query)
graph.add_node("resolver", resolve_software_node)
graph.add_node("error", error_end)
graph.add_node("clarification", clarification)
graph.add_node("allowed_softs", listing_allowed_software)
graph.add_node("web_search", web_searcher_node)
graph.add_node("html_generator", html_generator_node)

graph.add_edge(START, "normalizer")
graph.add_edge("normalizer", "resolver")
graph.add_conditional_edges(
    "resolver",
    route_after_resolver,
    {
        "error": "error",
        "clarification": "clarification",
        "allowed_software": "allowed_softs",
        "software_info": "web_search",
        "general_chat": "chatbot"
    }
    )

graph.add_edge("error", END)
graph.add_edge("clarification", END)
graph.add_edge("chatbot", END)
graph.add_edge("web_search", "html_generator")
graph.add_edge("html_generator", END)
graph.add_edge("allowed_softs", END)

app = graph.compile(checkpointer=MemorySaver())

