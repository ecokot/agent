# tools/file_tools.py
import os
from tools.registry import register_tool


def read_file(path: str):
    if not os.path.exists(path):
        return f"Файл не найден: {path}"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Файл записан: {path}"

def count_rows(path: str):
    if not os.path.exists(path):
        return f"Файл не найден: {path}"

    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

count_rows_schema = {
    "type": "function",
    "function": {
        "name": "count_rows",
        "description": "Подсчитать строки в файле",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Путь к файлу"
                }
            },
            "required": ["path"]
        }
    }
}


read_file_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Прочитать файл",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Путь к файлу"
                }
            },
            "required": ["path"]
        }
    }
}


write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Записать файл",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Путь к файлу"
                },
                "content": {
                    "type": "string",
                    "description": "Текст для записи"
                }
            },
            "required": ["path", "content"]
        }
    }
}


register_tool(read_file, read_file_schema)
register_tool(write_file, write_file_schema)
register_tool(count_rows, count_rows_schema)