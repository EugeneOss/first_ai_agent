from app.agent.state import AgentState

def error_end(state: AgentState) -> str:
    error = state.get("error")
    if error:
        return error
    return "Unknown error"
    