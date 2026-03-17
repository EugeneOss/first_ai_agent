from app.agent.state import AgentState

from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

web_searcher = TavilySearch(
            max_results=5,
            topic="general",
            include_answer=True,
            search_depth="advanced"
        )

def web_searcher_node(state: AgentState) -> dict:
    query = state.get("web_queries")
    query = query[0] if query else None
    
    if not query:
        return {}

    result = web_searcher.invoke({"query": query})
    
    top_results = result.get("results", [])[:3]

    sources = []
    contents = []

    for item in top_results:
        sources.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "score": item.get("score", 0.0),
            })
        contents.append(item.get("content", ""))

    return {"search_results":
            {
            "query": result.get("query", ""),
            "summary": result.get("answer", ""),
            "sources": sources,
            "retrieved_context": "\n\n".join(contents),
            }
        }