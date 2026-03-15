from typing import Annotated, Sequence, TypedDict, NotRequired

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

if OPENAI_API_KEY is None:
    raise ValueError("There isn't any api key")

# 0. Creating API-ref for LLM
model_qwen = ChatOpenAI(
    api_key = SecretStr(OPENAI_API_KEY),
    base_url = OPENROUTER_BASE_URL,
    model = "qwen/qwen-2.5-7b-instruct"
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    document_content: NotRequired[str]

@tool
def update(content:str) -> str:
    """Use this tool only when the full document content is ready.
    This tool replaces the entire current document with the provided text.
    
    Args:
        content (str): Full new text of the document
    """
    return content

@tool
def save(filename: str, content: str) -> str:
    """Save the current document to a text file and finish the process
    
    Args:
        filename (str): Name for the text file.
    """

    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    
    try:
        with open(filename, 'w') as file:
            file.write(content)
        return f"Document has been saved successfully to '{filename}'."
    
    except Exception as e:
        return f"Error saving document: {str(e)}"
    
tools = [update, save]
tool_model_qwen = model_qwen.bind_tools(tools=tools)

# agent node
def our_agent(state: AgentState) -> dict:
    "Node for chating with agent"
    system_prompt = SystemMessage(content=f"""You are Drafter, a helpful writing assistant.
Your job is to help the user create, update, and save text documents.

Rules:
- Use the `update` tool ONLY when you already have enough information to write or rewrite the document.
- If the user request is incomplete or ambiguous, ask a clarifying question first and DO NOT call any tool.
- Use the `save` tool ONLY when the user explicitly asks to save the document.
- When calling `update`, always pass the full new document content.
- When calling `save`, always pass:
  - `filename`: the requested filename
  - `content`: the current full document content
- If the user is just chatting or asking a general question, answer normally and do not call any tool.
- Never invent missing details such as recipient, tone, dates, names, or purpose unless the user explicitly allows you to draft a generic example.

Current document content:
{state.get("document_content", "")}
""")
    
    all_messages = [system_prompt] + list(state["messages"])
    response = tool_model_qwen.invoke(all_messages)

    return {"messages": [response]}

# document updating node
def update_document(state: AgentState) -> dict:
    messages = state["messages"]
    
    if not messages:
        return {}
    
    last_message = messages[-1]


    if (
        isinstance(last_message, ToolMessage)
        and last_message.name == "update"
        and isinstance(last_message.content, str)
    ):
        return {"document_content": last_message.content}
    return {}

# conditional edge
def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""

    messages = state["messages"]

    if not messages:
        return "continue"

    last_message = messages[-1]

    if isinstance(last_message, ToolMessage) and last_message.name == "save":
        return "end"

    return "continue"
    
def tools_router(state: AgentState) -> str:
    messages = state["messages"]

    if not messages:
        return "end"
    
    last_message = messages[-1]

    if (isinstance(last_message, AIMessage) and
        hasattr(last_message, "tool_calls") and
        last_message.tool_calls):
        return "tools"

    return "end"

graph = StateGraph(AgentState)

# nodes
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools=tools))
graph.add_node("update_document", update_document)

# edges
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    tools_router,
    {
        "end": END,
        "tools": "tools"
    }
)
graph.add_edge("tools", "update_document")
graph.add_conditional_edges(
    "update_document",
    should_continue,
    {
        "continue": "agent",
        "end": END
    }
)

app = graph.compile(checkpointer=MemorySaver())

cfg: RunnableConfig = {"configurable": {"thread_id": "id_0"}}

def run_document_agent():
    print("\n===== DRAFTER =====")
    print("Hello. I'm DRAFTER and I'm ready to help you create and update a document.")
    
    while True:
        user_text = input("\n> ").strip()

        if user_text.lower() == "exit":
            break

        if not user_text:
            continue

        before_len = 0
        state_snapshot = app.get_state(cfg)
        if state_snapshot and state_snapshot.values and "messages" in state_snapshot.values:
            before_len = len(state_snapshot.values["messages"])

        prev_len = before_len

        for event in app.stream(
            {"messages": [HumanMessage(content=user_text)]},
            stream_mode="values",
            config=cfg
        ):
            if "messages" in event and len(event["messages"]) > prev_len:
                msg = event["messages"][-1]
                if (
                    isinstance(msg, AIMessage)
                    and not getattr(msg, "tool_calls", None)
                    and isinstance(msg.content, str)
                    and msg.content.strip()
                ):
                    print(f"\n🤖 {msg.content}")
                
                prev_len = len(event["messages"])

        final_state = app.get_state(cfg).values
        messages = final_state["messages"]
        document_content = final_state.get("document_content", "")

        new_messages = messages[before_len:]
        last_tool_name = None

        for message in reversed(new_messages):
            if isinstance(message, ToolMessage):
                last_tool_name = message.name
                break

        if last_tool_name == "update":
            print("\nThe document has been updated successfully with content:\n")
            print(document_content)
        elif last_tool_name == "save":
            print("\nThe document has been saved successfully.")
            break

    print("\n===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_document_agent()