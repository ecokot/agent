# dialog_logger.py
import json
from pathlib import Path
from datetime import datetime


class DialogLogger:
    def __init__(self, dialog_dir="logs/dialogs", max_files=10, max_size_mb=1):
        self.dialog_dir = Path(dialog_dir)
        self.dialog_dir.mkdir(parents=True, exist_ok=True)
        self.max_files = max_files
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_file = None

    def _cleanup_old_files(self):
        files = sorted(self.dialog_dir.glob("dialog_*.jsonl"), key=lambda f: f.stat().st_mtime)

        while len(files) > self.max_files:
            files[0].unlink()
            files.pop(0)

    def _get_new_file(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.dialog_dir / f"dialog_{timestamp}.json"

    def _check_rotation(self):
        if self.current_file is None:
            return True

        if not self.current_file.exists():
            return True

        if self.current_file.stat().st_size >= self.max_size_bytes:
            return True

        return False

    def log_message(self, message):
        if self._check_rotation():
            self._cleanup_old_files()
            self.current_file = self._get_new_file()

            header = {
                "timestamp": datetime.now().isoformat(),
                "type": "dialog_start"
            }
            with self.current_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(header, ensure_ascii=False) + "\n")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }

        with self.current_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")