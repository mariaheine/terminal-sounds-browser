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
import time
import json
from pathlib import Path
from src.database import Database
from src.logger import Logger

version = "0.1.0"


class BBCCategories:
    def __init__(self, logger: Logger, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.database = Database(logger, db_path, verbose=True)
        #self.request_delay = 0.5
        self.headers = {
            f"User-Agent": "bbc-sound-browser/{version} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.bbc_url_api = "https://sound-effects-api.bbcrewind.co.uk/api/sfx"
        self.bbc_endpoint_aggregations_category = "/categoryAggregations"

        self.logger = logger
        self.logger.info("Accessing BBC Categories Menu")

        self.init_session()

    def init_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # TODO this is some relic of the past
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,  °
                  title TEXT NOT NULL CHECK(LENGTH(title) > 0),
                  url TEXT UNIQUE NOT NULL,
                  duration INTEGER CHECK(duration > 0),
                  added_date DATE DEFAULT (datetime('now')),
                  category TEXT DEFAULT 'uncategorized',
                  is_favorite BOOLEAN DEFAULT 0
                )
                """
            )

    #def search(self, query):
    #    time.sleep(self.request_delay)
    #    response = self.session.get(f"{base_url}", params={"q": query})

    def download_categories_data(self):
        payload = {
            "criteria": {
                "caregories": None,
                "durations": None,
                "from": 0,
                "size": 10,
            }
        }

        response = requests.post(
            f"{self.bbc_url_api}{self.bbc_endpoint_aggregations_category}",
            json=payload,
            headers=self.headers,
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
        #with sqlite3.connect(self.db_path) as conn:
         #   cursor = conn.cursor()
          #  cursor.execute("SELECT name, size FROM categories ORDER BY name")
           # categories = {name: size for name, size in cursor.fetchall()}
            #return categories
        query = "SELECT name, size FROM categories ORDER BY name"
        cursor = self.database.query(query)
        categories = {name: size for name, size in cursor.fetchall()}
        return categories
            
    def update_categories_cache(self):
        categories = self.download_categories_data()
        self.cache_categories_data(categories)
              
    def get_categories(self):
        if not self.check_categories_cache():
            self.update_categories_cache()
        categories = self.get_cached_categories()
        return categories
      
    #def get_cached_json(self, filename):
    #    path = Path(self.json_cache)
    #    filepath = path / f"{filename}.json"
    #    data = json.loads(filepath.read_text())
    #    return data

