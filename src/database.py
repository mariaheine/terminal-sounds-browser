import sqlite3
from pathlib import Path
from typing import Tuple
from src.logger import Logger

class Database:
    def __init__(self, db_path: Path, verbose=False):
        self.conn = sqlite3.connect(db_path)
        self.logger = Logger()
        self.verbose = verbose

    def execute(self, query, params = None, silent=True):

        cursor = self.conn.cursor()

        if self.verbose and not silent:
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            
            if params:
                cursor.execute(explain_query, params)
            else:
                cursor.execute(explain_query)

            plan = cursor.fetchall()

            self.logger.explain_query(query, plan)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        return cursor

    def commit(self):
        self.conn.commit()


