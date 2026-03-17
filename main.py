from app.agent.graph import app
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

print("""Привет, я агент, который может с тобой пообщаться, а также подготовить для тебя презентацию.
Если ты попросишь рассказать о каком-нибудь продукте, то я подготовлю такую презентация в формате кода HTML.
Тебе достаточно создать файл с названием 'presentation.html', скопировать текст кода и вставить в данный файл.
Сохранить и запустить в любом браузере.

Ну что, попробуем. Напиши мне что-нибудь.
Если захочешь прирвать разговор, просто напиши 'exit' или 'stop'
""")

user_input = input("User: ").strip()

cfg: RunnableConfig = {"configurable":{"thread_id": "current_session"}}

while user_input.strip().lower() not in ["stop", "exit"]:
    response = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=cfg)

    for message in reversed(response["messages"]):
        if isinstance(message, AIMessage):
            print(f"Assistant: {message.content}")    
            break
    user_input = input("\nUser: ").strip()
