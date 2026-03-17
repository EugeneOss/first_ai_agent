from app.agent.state import AgentState

def route_after_resolver(state: AgentState) -> str:
    if state.get("error"):
        return "error"

    if state.get("clarification_needed"):
        return "clarification"

    intent_type = state.get("intent_type")

    if intent_type == "allowed_software":
        return "allowed_software"

    if intent_type == "software_info":
        return "software_info"

    if intent_type == "general_chat":
        return "general_chat"

    return "error"