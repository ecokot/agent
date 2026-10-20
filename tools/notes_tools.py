# tools/notes_tools.py
import json
from pathlib import Path
from tools.registry import register_tool


NOTES_FILE = Path("data/notes.json")


def _load_notes():
    if not NOTES_FILE.exists():
        return []

    with NOTES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_notes(notes):
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with NOTES_FILE.open("w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(text: str):
    notes = _load_notes()
    notes.append(text)
    _save_notes(notes)
    return "Заметка добавлена"


def list_notes():
    notes = _load_notes()
    if not notes:
        return "Заметок нет"

    return "\n".join(notes)


add_note_schema = {
    "type": "function",
    "function": {
        "name": "add_note",
        "description": "Добавить заметку",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Текст заметки"
                }
            },
            "required": ["text"]
        }
    }
}


list_notes_schema = {
    "type": "function",
    "function": {
        "name": "list_notes",
        "description": "Показать все заметки",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


register_tool(add_note, add_note_schema)
register_tool(list_notes, list_notes_schema)