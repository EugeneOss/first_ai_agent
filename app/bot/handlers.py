import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters.command import Command
from aiogram.exceptions import TelegramBadRequest
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.graph import app


load_dotenv()

BOT_API_KEY = os.getenv("BOT_API_KEY")

if not BOT_API_KEY:
    raise ValueError("Не получен ключ API от бота")

bot = Bot(token=BOT_API_KEY)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

MAX_TG_TEXT = 4096
LOGS_DIR = Path("./app/bot/outputs")
OUTPUTS_DIR = Path("./app/bot/outputs")

LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def log_to_file(user_id: int, text: str) -> None:
    log_file = LOGS_DIR / f"{user_id}.txt"
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(text)


def is_html_content(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower().strip()

    html_markers = [
        "<!doctype html",
        "<html",
        "<head",
        "<body",
        "<style",
        "<script",
        "</html>",
    ]
    return any(marker in text_lower for marker in html_markers)


async def send_long_aware_answer(bot: Bot, chat_id: int, user_id: int, text: str) -> None:
    try:
        if is_html_content(text):
            file_path = OUTPUTS_DIR / f"{user_id}_presentation.html"
            file_path.write_text(text, encoding="utf-8")

            await bot.send_document(
                chat_id=chat_id,
                document=FSInputFile(file_path),
                caption="Готово. Отправляю HTML-файл."
            )
            return

        if len(text) <= MAX_TG_TEXT:
            await bot.send_message(chat_id=chat_id, text=text)
            return

        raise TelegramBadRequest(method=None, message="message is too long")

    except TelegramBadRequest as e:
        error_text = str(e).lower()

        if "message is too long" in error_text or len(text) > MAX_TG_TEXT:
            file_path = OUTPUTS_DIR / f"{user_id}_response.md"
            file_path.write_text(text, encoding="utf-8")

            await bot.send_document(
                chat_id=chat_id,
                document=FSInputFile(file_path),
                caption="Ответ получился слишком длинным, поэтому отправляю его файлом."
            )
            return

        raise


@dp.message(Command(commands=["start"]))
async def process_command_start(message: Message):
    user = message.from_user
    if user:
        user_name = user.full_name
        user_id = user.id

        text = f"""Привет, {user_name}! Я агент, который может с тобой пообщаться, а также подготовить для тебя презентацию.
Если ты попросишь рассказать о каком-нибудь продукте, то я подготовлю такую презентацию в формате кода HTML.
Тебе достаточно создать файл с названием 'presentation.html', скопировать текст кода и вставить в данный файл.
Сохранить и запустить в любом браузере.
Если хочешь узнать, для каких программ я могу подготовить презентации, просто спроси "какие программы можно использовать?" или "какие программы разрешены?"

Ну что, попробуем. Напиши мне что-нибудь.
"""

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_to_file(
            user_id,
            f"\n[{now}] Пользователь {user_id} / {user_name} зарегистрировался в системе\n"
        )

        logging.info(f"{user_name} {user_id} запустил бота")
        await bot.send_message(chat_id=user_id, text=text)


@dp.message()
async def send_message_handler(message: Message):
    user = message.from_user
    if user:
        user_name = user.full_name
        user_id = user.id
        text = message.text or ""

        cfg: RunnableConfig = {
            "configurable": {
                "thread_id": str(user_id)
            }
        }

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_to_file(user_id, f"\n[{now}] User: {text}\n")

        logging.info(f"{user_name} {user_id} направил следующий текст: {text}")

        response = await app.ainvoke(
            {"messages": [HumanMessage(content=text)]},
            config=cfg
        )

        ai_answer = "Не удалось получить ответ от модели."

        for msg in reversed(response["messages"]):
            if isinstance(msg, AIMessage):
                ai_answer = str(msg.content)
                break

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_to_file(user_id, f"[{now}] Assistant: {ai_answer}\n")

        await send_long_aware_answer(
            bot=bot,
            chat_id=user_id,
            user_id=user_id,
            text=ai_answer
        )


if __name__ == "__main__":
    dp.run_polling(bot)