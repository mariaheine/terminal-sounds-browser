"""
A little tool to browse bbc sound effect library.

Check their robots.txt (at https://sound-effects.bbcrewind.co.uk/robots.txt) before using, at the time of making:

# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:

In any case this tool does not support bulk download of samples.
"""

import requests
import sys
import sqlite3
from pathlib import Path
from backend.src.utils.database import Database
from backend.src.utils.logger import Logger
from backend.src.constants import HEADERS, BBC_DATABASE, BBC_URL_API, BBC_API_CATEGORY_AGGREGATIONS_ENDPOINT

class BBCCategories:
    def __init__(self):
        self.db_path = BBC_DATABASE
        # self.db_path.parent.mkdir(parents=True, exist_ok=True) # TODO make note on this parent when file thing and delete
        self.logger = Logger()
        self.database = Database(BBC_DATABASE, verbose=True)

        self.logger.info("Accessing BBC Categories Menu")

        if not self.check_categories_cache():
            self.update_categories_cache()

    def update_categories_cache(self):
        categories = self.download_categories_data()
        self.cache_categories_data(categories)

    def download_categories_data(self):
        payload = {
            "criteria": {
                "caregories": None,
                "durations": None,
                "from": 0,
                "size": 10, # TODO should we assume that
            }
        }

        response = requests.post(
            f"{BBC_URL_API}{BBC_API_CATEGORY_AGGREGATIONS_ENDPOINT}",
            json=payload,
            headers=HEADERS
        )

        if response.status_code == 200:

            data = response.json()
            
            # structure of response body:
            # {
            #   "aggregations": {
            #     "Nature": {"doc_count": 17630},  
            #     "Bells": {"doc_count": 261},  
            #     # ...
            #   }
            # }

            categories = {
                key: value["doc_count"] for key, value in data["aggregations"].items()
            }

            return categories
        else:
            # TODO handle
            print("failed")
            sys.exit(1)

    def cache_categories_data(self, categories):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # First execute: CREATE TABLE
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE CHECK(LENGTH(name) > 0),
                  size INTEGER CHECK(size > 0),
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

            # AFTER UPDATE ON categories → Trigger fires when ANY row is UPDATED
            # NEW.id refers to the ID of the row that was just updated
            # WHERE id = NEW.id ensures we ONLY update the timestamp on THAT specific row
            
            # Second execute: CREATE TRIGGER
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
                AFTER UPDATE ON categories
                BEGIN
                    UPDATE categories SET last_updated = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
                """)

            for key, val in categories.items():
                # This will also neatly update timestamps
                cursor.execute(
                    "INSERT OR REPLACE INTO categories (name, size) VALUES (?,?)",
                    (key, val),
                )

            conn.commit()
            
    def check_categories_cache(self, max_age_days = 7):
      with sqlite3.connect(self.db_path) as conn:
          cursor = conn.cursor()
          
          # check if table exists
          cursor.execute("""
              SELECT name FROM sqlite_master 
              WHERE type='table' AND name='categories'
          """)

          # table missing, need to download 
          if not cursor.fetchone():
              #print("📦 Categories cache doesn't exist, got to runterladen meow!")
              return False  
              
          # table exists, try to use it
          try:
              # MAX(last_updated) = the most recent timestamp
              # returns just one val obvs
              cursor.execute("""
                  SELECT COUNT(*), MAX(last_updated) 
                  FROM categories
              """)

              count, last_updated = cursor.fetchone()
              
              if count == 0:
                  return False
              
              # here we use the MAX(last_updated)
              if last_updated:
                  cursor.execute("""
                      SELECT julianday('now') - julianday(?)
                  """, (last_updated,))
                  days_old = cursor.fetchone()[0]
                  
                  if days_old > max_age_days:
                      #print(f"📦 Cache is {days_old:.0f} days old - refreshing")
                      return False
                      
              return True
              
          except sqlite3.OperationalError:
              return False
            

    def get_cached_categories(self):
        query = "SELECT name, size FROM categories ORDER BY name"
        cursor = self.database.execute(query)
        categories = {name: size for name, size in cursor.fetchall()}
        return categories
            
              
    def get_categories(self):
        categories = self.get_cached_categories()
        return categories
      
    #def get_cached_json(self, filename):
    #    path = Path(self.json_cache)
    #    filepath = path / f"{filename}.json"
    #    data = json.loads(filepath.read_text())
    #    return data

