from app.agent.state import AgentState
from pathlib import Path
from models.models import llm_big
from langchain_core.messages import SystemMessage, HumanMessage

PROJECT_PATH = Path(__file__).resolve().parents[3]

with open(PROJECT_PATH / "prompts" / "html_prompt.txt", "r", encoding="utf-8") as file:
    prompt = file.read()

def html_generator_node(state: AgentState) -> dict:
    search_data = state.get("search_results", {})

    summary = search_data.get("summary", "")
    retrieved_context = search_data.get("retrieved_context", "")
    sources = search_data.get("sources", [])
    
    resolved_software = state.get("resolved_software") or {}
    product_name = resolved_software.get("name", "Неизвестный продукт")
    

    sources_text = "\n".join(
        f"- {item.get('title', '')}: {item.get('url', '')}"
        for item in sources
    )

    user_prompt = f"""
Название продукта: {product_name}

Краткая сводка:
{summary}

Контекст из источников:
{retrieved_context}

Источники:
{sources_text}

Сформируй HTML-страницу строго по системному промпту.
Используй только факты из контекста выше.
Весь текст страницы должен быть только на русском языке.
Верни только HTML.
"""

    response = llm_big.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=user_prompt),
    ])

    return {
        "messages": [response],
        "html_result" : response.content
        }