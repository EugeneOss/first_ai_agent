from typing import Annotated, Optional, Union, NotRequired, Required, Sequence, TypedDict

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from pydantic import SecretStr

from operator import add
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
POLZA_API_KEY = os.getenv("POLZA_API_KEY")
POLZA_BASE_URL = os.getenv("POLZA_BASE_URL")


if OPENAI_API_KEY is None:
    raise ValueError("There isn't any api key")
if POLZA_API_KEY is None:
    raise ValueError("There isn't any api key")

# 0. Creating API-ref for LLM
model_qwen = ChatOpenAI(
    api_key = SecretStr(OPENAI_API_KEY),
    base_url = OPENROUTER_BASE_URL,
    model = "qwen/qwen-2.5-7b-instruct"
)

model_polza_openai = ChatOpenAI(
    api_key = SecretStr(POLZA_API_KEY),
    base_url = POLZA_BASE_URL,
    model = "gpt-4o"
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def adding(a: int, b: int) -> int:
    """
    Description:
        This is a addition function that adds two numbers together
    
    Args:
        a (int): The first number
        b (int): The second number
    
    Output:
        The result of the addition.
    """
    return a + b

tools = [adding]

model_with_tools = model_polza_openai.bind_tools(tools)

# Creating nodes
def model_call(state: AgentState) -> dict[str, list[BaseMessage]]:
    """This is the agent which may chating with user"""
    system_prompt = SystemMessage(content="You are my AI assistant. You name is Jonatan. Please answer my query to the best of your ability.")
    user_message = state["messages"]
    response = model_with_tools.invoke(
        [system_prompt] + list(user_message)
    )
    return {"messages": [response]}

def router_function(state: AgentState):
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"

graph = StateGraph(AgentState)

graph.add_node("chatbot", model_call)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chatbot")
graph.add_conditional_edges(
    "chatbot",
    router_function,
    {
        "tools": "tools",
        "__end__": END
    }
)
graph.add_edge("tools", "chatbot")

app = graph.compile(checkpointer=MemorySaver())

cfg: RunnableConfig = {"configurable":{"thread_id": "id_0"}}

user_message = [HumanMessage(content = input("Enter: "))]
