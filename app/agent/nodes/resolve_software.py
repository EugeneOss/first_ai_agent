from pathlib import Path
from typing import Any

import yaml

from app.agent.state import AgentState
from models.models import intent_classifier_llm
from langchain_core.messages import HumanMessage, SystemMessage


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ALLOWED_SOFTWARE_PATH = PROJECT_ROOT / "data" / "allowed_software.yaml"


def load_alias_map() -> dict[str, dict[str, Any]]:
    software_by_alias: dict[str, dict[str, Any]] = {}

    with open(ALLOWED_SOFTWARE_PATH, "r", encoding="utf-8") as file:
        items = yaml.safe_load(file)["software"]

    for item in items:
        for alias in item["aliases"] + item["ru_aliases"]:
            software_by_alias[alias.lower()] = item

    return software_by_alias


SOFTWARE_BY_ALIAS = load_alias_map()


def _extract_matched_softwares(normalized_query: str) -> list[dict[str, Any]]:
    if not normalized_query:
        return []

    unigrams = normalized_query.split()
    bigrams = [
        f"{unigrams[i]} {unigrams[i + 1]}"
        for i in range(len(unigrams) - 1)
    ]

    matched: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    # Сначала биграммы
    for bg in bigrams:
        item = SOFTWARE_BY_ALIAS.get(bg)
        if item:
            unique_key = item.get("name", str(item))
            if unique_key not in seen_names:
                matched.append(item)
                seen_names.add(unique_key)

    # Потом униграммы
    for ug in unigrams:
        item = SOFTWARE_BY_ALIAS.get(ug)
        if item:
            unique_key = item.get("name", str(item))
            if unique_key not in seen_names:
                matched.append(item)
                seen_names.add(unique_key)

    return matched

with open(PROJECT_ROOT / "prompts" / "validation_prompt.txt", "r", encoding="utf-8") as file:
    text = file.read()

system_prompt = [SystemMessage(content=text)]

def resolve_software_node(state: AgentState) -> dict[str, Any]:
    try:
        normalized_query = state.get("normalized_query", "").strip()

        if not normalized_query:
            return {
                "intent_type": None,
                "matched_softwares": [],
                "resolved_software": None,
                "clarification_needed": False,
                "error": "normalized_query_is_empty",
                "web_queries": []
            }
    
        matched_softwares = _extract_matched_softwares(normalized_query)

        if not matched_softwares:
            return {
                "intent_type": "general_chat",
                "matched_softwares": [],
                "resolved_software": None,
                "clarification_needed": False,
                "error": None,
                "needs_web_search": False,
                "web_queries": []
            }
        
        if len(matched_softwares) > 1:
            return {
                "intent_type": None,
                "matched_softwares": matched_softwares,
                "resolved_software": None,
                "clarification_needed": True,
                "error": None,
                "needs_web_search": False,
                "web_queries": []
            }
        
        intent_result = intent_classifier_llm.invoke(
            system_prompt + [HumanMessage(content=normalized_query)]
        )

        resolved_software = matched_softwares[0]

        input_type = getattr(intent_result, "input_type", None)

        if input_type == "allowed_softwares_query":
            final_intent = "allowed_software"
            needs_web_search = False
            web_queries = []
        else:
            final_intent = "software_info"
            needs_web_search = True
            web_queries = resolved_software["search_queries"]

        return {
            "intent_type": final_intent,
            "matched_softwares": matched_softwares,
            "resolved_software": resolved_software,
            "clarification_needed": False,
            "error": None,
            "needs_web_search": needs_web_search,
            "web_queries": web_queries
        }
        

    except Exception as e:
        return {
            "intent_type": None,
            "matched_softwares": [],
            "resolved_software": None,
            "clarification_needed": False,
            "error": f"resolve_software_failed: {e}",
            "needs_web_search": False
        }