from pathlib import Path
from datetime import datetime
from typing import List, Tuple

class Logger:
    def __init__(self, cache_dir: Path):
        self.log_dir = cache_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"last.log"

        self.log_path = self.log_dir / log_file

    def _write(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level} {message}"

        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

    def debug(self, message):
        self._write("[🧼 DEBUG]", message) 

    def info(self, message):
        self._write("[🌬️ INFO]", message)

    def warning(self, message):
        self._write("[🎱 WARNING]", message)

    def explain_query(self, query: str, rows: List[Tuple]):
        msg = "\n- Query:\n"
        msg += query
        msg += "\n- Plan:\n"
        for row in rows:
            msg += f"{row}\n"
        self._write("[🧭 QUERY PLAN]", msg)
