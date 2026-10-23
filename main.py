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
model = "qwen3.5:9b"
# model = "qwen3.8"

instructions = """
Ты — ИИ-агент. Отвечай на русском языке.
Отвечай коротко, по-русски, без markdown и emoji.
Выдавай только финальный ответ.

Файловый протокол:
1. Не угадывай пути файлов.
2. Сначала используй list_directory или find_files, чтобы узнать точный путь.
3. Если нужно найти текст внутри известного файла, используй search_in_file.
4. read_file используй только когда точный путь уже известен.
5. Не читай большие файлы целиком. Сначала используй count_rows или search_in_file.
6. Если подходящего инструмента нет, скажи: нет подходящего инструмента.
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
print(assistant("найди и выведи функцию write_file на какой  она строке в файле code.txt"))


