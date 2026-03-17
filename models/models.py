from dotenv import load_dotenv
import os
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from .schemas import IntentClassification

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
POLZA_API_KEY = os.getenv("POLZA_API_KEY")
POLZA_BASE_URL = os.getenv("POLZA_BASE_URL")

if not OPENAI_API_KEY:
    raise ValueError("API ключ для модели не найден. Проверьте наличие ключа или обратитесь к администратору")

if not POLZA_API_KEY:
    raise ValueError("API ключ для модели не найден. Проверьте наличие ключа или обратитесь к администратору")


llm_small = ChatOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key = SecretStr(OPENAI_API_KEY),
    model = "qwen/qwen2.5-coder-7b-instruct",
    temperature=0
)


llm_mid = ChatOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key = SecretStr(OPENAI_API_KEY),
    model = "qwen/qwen-2.5-72b-instruct",
    temperature=0
)


llm_big = ChatOpenAI(
    base_url=POLZA_BASE_URL,
    api_key = SecretStr(POLZA_API_KEY),
    model = "openai/gpt-5.1",
    temperature=0
)


simple_html_llm = ChatOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key = SecretStr(OPENAI_API_KEY),
    model = "qwen/qwen2.5-coder-7b-instruct",
    temperature=0
)


strong_html_llm = ChatOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key = SecretStr(OPENAI_API_KEY),
    model = "qwen/qwen-2.5-coder-32b-instruct",
    temperature=0
)

intent_classifier_llm = llm_small.with_structured_output(IntentClassification)