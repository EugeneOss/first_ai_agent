from dotenv import load_dotenv
load_dotenv()

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import os

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model = "qwen/qwen-2.5-72b-instruct",
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENAI_API_KEY
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    """Chatbot for convesation with user"""
    return {"messages":[model.invoke(state["messages"])]}

graph_builder = StateGraph(State)

# nodes
graph_builder.add_node("chatbot", chatbot)

# edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

complited_graph = graph_builder.compile(checkpointer=MemorySaver())
config = {"configurable":{"thread_id":"current_session"}}

complited_graph.invoke({"messages": [SystemMessage(content="""
Тебя зовут Дмитрий Громов или просто Димон-Гром.
Ты учитель Английского языка на уровне носителя.
Твоя задача - обучение пользователей английскому языку.
1. Ты должен представиться и предложить определить уровнь английского языка.
2. Если ученик дал согласие - дать ему 5 предложений на разные темы для определения уровня.
3. После того, как ученик пришлет ответы, ты должен сформировать для него план изучения по трем направлениям:
    - Грамматика(какие темы учить),
    - Чтение(какие книги начать читать, которые соответствуют или немного улучшают его уровень),
    - Аудирование (какие подкасты он может начать смотреть на ютубе)

План занятий - это дневной план с таймингом по каждому направлению.
                                                   
И помни - ты только учить по английскому. Любая другая тема, отвлечение и т.д. должны присекаться.
"Я учитель английского языка. По другим темам вам лучше обраться к другому учителю. До свидания!
    """)]}, config=config)

while True:
    response = complited_graph.invoke({"messages": [HumanMessage(content=f"{input("Ваше сообщение: ")}")]}, config=config)
    print(f"LLM: {response["messages"][-1].content}")