from app.agent.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from models.models import llm_big, llm_mid, llm_small, simple_html_llm, strong_html_llm

def low_chatbot(state: AgentState) -> dict:
    "Chatbot with 'qwen2.5-coder-7b-instructions' model"
    messages = state.get("messages", [])
    response = llm_small.invoke(messages)
    return {
        "messages": [response]
    }

def mid_chatbot(state: AgentState) -> dict:
    "Chatbot with 'qwen-2.5-72b-instruct' model"
    messages = state.get("messages", [])
    response = llm_mid.invoke(messages)
    return {
        "messages": [response]
    }

def strong_chatbot(state: AgentState) -> dict:
    "Chatbot with 'GPT 5.1' model"
    messages = state.get("messages", [])
    response = llm_big.invoke(messages)
    return {
        "messages": [response]
    }

def simple_html_gen(state: AgentState) -> dict:
    "Chatbot with 'qwen2.5-coder-7b-instruct' model"
    messages = state.get("messages", [])
    response = simple_html_llm.invoke(messages)
    return {
        "messages": [response]
    }

def strong_html_gen(state: AgentState) -> dict:
    "Chatbot with 'GPT 5.1' model"
    messages = state.get("messages", [])
    response = strong_html_llm.invoke(messages)
    return {
        "messages": [response]
    }
    