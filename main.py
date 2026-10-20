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

# model = "qwen3.5:0.8b"
# model = "qwen3.5:4b"
# model = "qwen3.5:9b"
model = "qwen3.8"

instructions = """
Ты — ИИ-агент.
Выдавай только финальный ответ.
"""

# instructions = """
# Ты — ИИ-агент.
# Отвечай коротко, по-русски, без markdown и emoji.
# Если не знаешь ответа — используй ТОЛЬКО доступные инструменты.
# Если нет подходящего инструмента — скажи, нет подходящего инструмента.
# Только инструменты дают истину.
# Выдавай только финальный ответ.
# """


tools, functions = get_tools([
    "read_file",
    "write_file",
    "count_rows",
    "list_directory"
])

assistant = Assistant(
    client=client,
    model=model,
    instructions=instructions,
    tools=tools,
    functions=functions,
)
print(assistant("Выведи текст из файла заяц.txt в консоль"))

