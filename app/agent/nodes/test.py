from models.models import llm_mid
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk

user_input = input("="*10 + " User " + "="*10 + "\n")
# print('-'*40)


while user_input not in ['exit', 'stop']:
    print("="*10 + " AI " + "="*10)
    for chunk in llm_mid.stream([HumanMessage(content = user_input)]):
        print(chunk.content, end="", flush=True)
    print()
    user_input = input("="*10 + " User " + "="*10 + "\n")
    # print('-'*40)