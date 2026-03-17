import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from src.backend.constants import LOGS_DIR, LOG_FILE_NAME

class Logger:
    def __init__(self):
        self.log_path = LOGS_DIR / LOG_FILE_NAME

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

    def error(self, message):
        self._write("[🧨 ERROR]", message)

    def explain_query(self, query: str, rows: List[Tuple]):
        msg = "\n- Query:\n"
        msg += query
        msg += "\n- Plan:\n"
        for row in rows:
            msg += f"{row}\n"
        self._write("[🧭 QUERY PLAN]", msg)

if __name__ == "main":
    logger = Logger()
    logger.error("derp")
    parser = argparse.ArgumentParser("Logger Parser")
    parser.add_argument("level")
    parser.add_argument("message")

    args = parser.parse_args()
    level = args.level
    message = args.message

    if level == "info":
        logger.info(message)
    elif level == "debug":
        logger.debug(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.error(f"Unhandled log type: {level}")
    
