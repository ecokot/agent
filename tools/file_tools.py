# tools/file_tools.py
import os
import re
from pathlib import Path
from tools.registry import register_tool
from config import (
    BASE_DIR,
    MAX_FILE_READ_SIZE_MB,
    MAX_FILE_WRITE_SIZE_MB,
    MAX_LIST_DEPTH,
    MAX_LIST_FILES,
    MAX_SEARCH_RESULTS,
    MAX_SEARCH_LINE_LENGTH
)


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

    file_size_mb = validated_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_READ_SIZE_MB:
        return f"File too large ({file_size_mb:.1f}MB, max {MAX_FILE_READ_SIZE_MB}MB)"

    with open(validated_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str, mode: str = "overwrite",
               pattern: str = None, replacement: str = None,
               insert_index: int = None, case_sensitive: bool = True):
    """
    Запись в файл с разными режимами.

    Args:
        path: Относительный путь к файлу
        content: Контент для записи
        mode: Режим записи (overwrite, append, prepend, replace, insert)
        pattern: Шаблон для поиска (для режима replace)
        replacement: Текст для замены (для режима replace, по умолчанию content)
        insert_index: Индекс строки для вставки (для режима insert, 0-based)
        case_sensitive: Чувствительность к регистру (для режима replace)
    """
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    # Проверяем размер контента для записи
    content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
    if content_size_mb > MAX_FILE_WRITE_SIZE_MB:
        return f"Content too large ({content_size_mb:.1f}MB, max {MAX_FILE_WRITE_SIZE_MB}MB)"

    validated_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Читаем существующий контент если файл существует
        existing_content = ""
        if validated_path.exists():
            with open(validated_path, "r", encoding="utf-8") as f:
                existing_content = f.read()

        if mode == "overwrite":
            new_content = content

        elif mode == "append":
            new_content = existing_content + content

        elif mode == "prepend":
            new_content = content + existing_content

        elif mode == "insert":
            if insert_index is None:
                return "insert_index required for insert mode"

            lines = existing_content.splitlines(keepends=True)

            if insert_index < 0 or insert_index > len(lines):
                return f"Invalid insert_index: {insert_index}. File has {len(lines)} lines"

            lines.insert(insert_index, content + "\n")
            new_content = "".join(lines)

        elif mode == "replace":
            if pattern is None:
                return "pattern required for replace mode"

            if replacement is None:
                replacement = content

            flags = 0 if case_sensitive else re.IGNORECASE

            try:
                compiled = re.compile(pattern, flags)
            except re.error as e:
                return f"Invalid regex pattern: {e}"

            if not compiled.search(existing_content):
                return f"No matches found for pattern '{pattern}'"

            new_content = compiled.sub(replacement, existing_content)

        else:
            return f"Unknown mode: {mode}. Use: overwrite, append, prepend, replace, insert"

        with open(validated_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"File written: {path} (mode: {mode})"

    except Exception as e:
        return f"Error: {e}"


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


def search_in_file(path: str, pattern: str, mode: str = "regex",
                   max_results: int = MAX_SEARCH_RESULTS,
                   case_sensitive: bool = True):
    """
    Поиск в файле с разными режимами.

    Args:
        path: Относительный путь к файлу
        pattern: Шаблон поиска
        mode: Режим поиска (regex, contains, exact, word)
        max_results: Максимум результатов
        case_sensitive: Чувствительность к регистру
    """
    try:
        validated_path = _resolve_path(path)
    except ValueError as e:
        return str(e)

    if not validated_path.exists():
        return f"File not found: {path}"

    if validated_path.stat().st_size > 10 * 1024 * 1024:
        return "File too large (max 10MB)"

    try:
        with open(validated_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        return f"Error reading file: {e}"

    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        if mode == "regex":
            compiled = re.compile(pattern, flags)
        elif mode == "contains":
            escaped = re.escape(pattern)
            compiled = re.compile(escaped, flags)
        elif mode == "exact":
            escaped = re.escape(pattern)
            compiled = re.compile(f"^{escaped}$", flags)
        elif mode == "word":
            escaped = re.escape(pattern)
            compiled = re.compile(rf"\b{escaped}\b", flags)
        else:
            return f"Unknown mode: {mode}. Use: regex, contains, exact, word"
    except re.error as e:
        return f"Invalid regex pattern: {e}"

    results = []
    for line_num, line in enumerate(lines, 1):
        if len(results) >= max_results:
            results.append(f"... (limit {max_results} results)")
            break

        matches = list(compiled.finditer(line))
        if matches:
            display_line = line.rstrip('\n')
            if len(display_line) > MAX_SEARCH_LINE_LENGTH:
                display_line = display_line[:MAX_SEARCH_LINE_LENGTH] + "..."

            match_positions = [f"{m.start()}-{m.end()}" for m in matches]
            results.append(f"Line {line_num} [matches: {', '.join(match_positions)}]: {display_line}")

    if not results:
        return f"No matches found for pattern '{pattern}'"

    return f"Found {len(results)} match(es):\n" + "\n".join(results)


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
                },
                "mode": {
                    "type": "string",
                    "enum": ["overwrite", "append", "prepend", "replace", "insert"],
                    "description": "Write mode (default: overwrite)"
                },
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern for replace mode"
                },
                "replacement": {
                    "type": "string",
                    "description": "Replacement text for replace mode (default: content)"
                },
                "insert_index": {
                    "type": "integer",
                    "description": "0-based line index for insert mode"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive for replace mode (default: true)"
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

search_in_file_schema = {
    "type": "function",
    "function": {
        "name": "search_in_file",
        "description": "Search for pattern in file using different modes",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to file"
                },
                "pattern": {
                    "type": "string",
                    "description": "Search pattern"
                },
                "mode": {
                    "type": "string",
                    "enum": ["regex", "contains", "exact", "word"],
                    "description": "Search mode: regex (regular expression), contains (substring), exact (full line match), word (whole word)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive search (default: true)"
                }
            },
            "required": ["path", "pattern", "mode"]
        }
    }
}


register_tool(read_file, read_file_schema)
register_tool(write_file, write_file_schema)
register_tool(count_rows, count_rows_schema)
register_tool(list_directory, list_directory_schema)
register_tool(search_in_file, search_in_file_schema)
