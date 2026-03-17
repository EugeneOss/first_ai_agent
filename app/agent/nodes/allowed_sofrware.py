from app.agent.state import AgentState
from langchain_core.messages import AIMessage
import yaml
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[3]

with open(PROJECT_PATH / "data" / "allowed_software.yaml", "r", encoding="utf-8") as file:
    allowed_softs = yaml.safe_load(file)

all_softs = "\n".join({el['name'] for el in allowed_softs['software']})

def listing_allowed_software(state:AgentState) -> dict:
    text = f"Ниже программы, которые доступны у нас в компании:\n{all_softs}"
    message = AIMessage(content=text)
    
    return {"messages": [message]}