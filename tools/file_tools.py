# tools/file_tools.py
import os
from pathlib import Path
from tools.registry import register_tool
from config import BASE_DIR, MAX_LIST_DEPTH, MAX_LIST_FILES


def _resolve_path(path: str) -> Path:
    """Преобразует относительный путь в абсолютный внутри BASE_DIR"""
    if os.path.isabs(path):
        raise ValueError(f"Use relative paths only. Workspace root: {BASE_DIR}")

    resolved = (BASE_DIR / path).resolve()

    if not str(resolved).startswith(str(BASE_DIR)):
        raise ValueError(f"Access denied: path escapes workspace. Use relative path from: {BASE_DIR}")

    return resolved


def _format_size(size_bytes: int) -> str:
    """Форматирует размер файла"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def read_file(path: str):
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    if not validated_path.exists():
        return f"File not found: {path}"

    with open(validated_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    validated_path.parent.mkdir(parents=True, exist_ok=True)

    with open(validated_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written: {path}"


def count_rows(path: str):
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    if not validated_path.exists():
        return f"File not found: {path}"

    with open(validated_path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def list_directory(path: str = ".", recursive: bool = False,
                   max_depth: int = MAX_LIST_DEPTH,
                   max_files: int = MAX_LIST_FILES):
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    if not validated_path.exists():
        return f"Directory not found: {path}"

    if not validated_path.is_dir():
        return f"Not a directory: {path}"

    try:
        result = []
        file_count = 0

        def _walk(current_path: Path, depth: int):
            nonlocal file_count

            if depth > max_depth or file_count >= max_files:
                return

            try:
                items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                result.append(f"{'  ' * depth}[permission denied]")
                return

            for item in items:
                if file_count >= max_files:
                    result.append(f"{'  ' * depth}... (limit {max_files} files)")
                    break

                rel_path = item.relative_to(validated_path)

                if item.is_dir():
                    result.append(f"{'  ' * depth}[DIR] {rel_path}/")
                    if recursive:
                        _walk(item, depth + 1)
                else:
                    size = item.stat().st_size
                    size_str = _format_size(size)
                    result.append(f"{'  ' * depth}[FILE] {rel_path} ({size_str})")

                file_count += 1

        _walk(validated_path, 0)

        if not result:
            return "Directory is empty"

        return "\n".join(result)

    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error: {e}"


count_rows_schema = {
    "type": "function",
    "function": {
        "name": "count_rows",
        "description": "Count lines in a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to file"
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
        "description": "Read a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to file"
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
        "description": "Write content to a file (creates parent directories if needed)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                }
            },
            "required": ["path", "content"]
        }
    }
}


list_directory_schema = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List files and directories in the workspace",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative directory path (default: current directory)"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "List recursively (default: false)"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum recursion depth (default: 3)"
                },
                "max_files": {
                    "type": "integer",
                    "description": "Maximum files in output (default: 100)"
                }
            },
            "required": []
        }
    }
}


register_tool(read_file, read_file_schema)
register_tool(write_file, write_file_schema)
register_tool(count_rows, count_rows_schema)
register_tool(list_directory, list_directory_schema)