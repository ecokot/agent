# main.py
from logger import setup_logger
setup_logger()

from openai import OpenAI

from assistant import Assistant
from tools.registry import get_tools


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODELS = [
    "qwen3.5:0.8b",
    "qwen3.5:4b",
    "qwen3.5:9b",
    "qwen3.8",
]

model = "qwen3.5:4b"

instructions = """
Ты — ИИ-агент.

1. Отвечай на русском языке, коротко, без markdown и emoji.
2. ВСЕГДА используй доступные инструменты для получения информации.
3. Никогда не выдумывай содержимое файлов или путей.
4. Выдавай только финальный ответ, без пояснений.

"""

tools, functions = get_tools([
    "read_file",
    "write_file",
    "list_directory",
    "search_in_file",
])

assistant = Assistant(
    client=client,
    model=model,
    instructions=instructions,
    tools=tools,
    functions=functions,
)
print(assistant("найди функцию write_file и напиши на какой она строке в файле cote.txt"))


