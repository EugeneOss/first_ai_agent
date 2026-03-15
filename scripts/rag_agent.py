from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Sequence, Annotated, NotRequired
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage, AIMessageChunk
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig

load_dotenv()

POLZA_API_KEY = os.getenv("POLZA_API_KEY")
POLZA_BASE_URL = os.getenv("POLZA_BASE_URL")

if not POLZA_API_KEY:
    raise ValueError("There isn't any api key!")

model = ChatOpenAI(
    model="openai/gpt-4o",
    api_key=SecretStr(POLZA_API_KEY),
    base_url=POLZA_BASE_URL,
    temperature=0
)

model_emb = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=SecretStr(POLZA_API_KEY),
    base_url=POLZA_BASE_URL
)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph = StateGraph(AgentState)

def chatbot(state: AgentState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

graph.add_node("chatbot", chatbot)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile(checkpointer=MemorySaver())
cfg: RunnableConfig = {"configurable": {"thread_id": "current_id"}}

print("Hello. You can initialize the chat with a message or write 'exit' to exit.")
user_input = input("====== User ======\n")
user_message = HumanMessage(content=user_input)

while user_input != "exit":
    print("====== AI ======")
    for event in app.stream({"messages":[user_message]}, config=cfg, stream_mode="messages"):
        message, metadata = event
        if isinstance(message, AIMessageChunk) and hasattr(message, "content") and message.content:
            print(message.content, end="", flush=True)
    
    user_input = input("\n====== User ======\n")
    user_message = HumanMessage(content=user_input)