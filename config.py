from pathlib import Path

BASE_DIR = (Path(__file__).parent / "workspace").resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Лимиты для файловых инструментов
MAX_LIST_DEPTH = 3
MAX_LIST_FILES = 100
MAX_FILE_READ_SIZE_MB = 10
MAX_FILE_WRITE_SIZE_MB = 50