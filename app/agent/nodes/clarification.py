from app.agent.state import AgentState
from langchain_core.messages import AIMessage

def clarification(state:AgentState) -> dict:
    text = (
        "Я могу обработать только одну программу, поэтому прошу выбрать одну "
        "из указанных и написать: 'Расскажи о программе <название программы>'"
    )
    message = AIMessage(content=text)
    
    return {"messages": [message]}