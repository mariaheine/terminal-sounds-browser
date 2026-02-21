"""
A little tool to browse bbc sound effect library.

Check their robots.txt (at https://sound-effects.bbcrewind.co.uk/robots.txt) before using, at the time of making:

# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:

In any case this tool does not support bulk download of samples.
"""

import requests

# from bs4 import BeautifulSoup # docs here: https://beautiful-soup-4.readthedocs.io/en/latest/
# from playwright.sync_api import sync_playwright
import sys
import sqlite3
import time
import json
import subprocess
from pathlib import Path

version = "0.1.0"


class AudioDatabase:
    def __init__(self):
        self.db_path = "data/bbc.db"
        self.request_delay = 0.5
        self.json_cache = "cache/json"
        self.sound_cache = "cache/sound"

        # requests
        self.headers = {
            f"User-Agent": "bbc-sound-browser/{version} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.bbc_url_api = "https://sound-effects-api.bbcrewind.co.uk/api/sfx"
        self.bbc_endpoint_search = "/search"
        self.bbc_endpoint_aggregations_category = "/categoryAggregations"

        self.init_session()

    def init_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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

    def search(self, query):
        time.sleep(self.request_delay)
        response = self.session.get(f"{base_url}", params={"q": query})

    def download_bbc_categories(self):
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
            print("💽 yas")
            data = response.json()
            # print(data)
            """
            structure of response body:
            {
              "aggregations": {
                "Nature": {"doc_count": 17630},  
                "Bells": {"doc_count": 261},  
                # ...
              }
            }
            """
            categories = {
                key: value["doc_count"] for key, value in data["aggregations"].items()
            }

            return categories
        else:
            # TODO handle
            print("failed")
            sys.exit(1)

    def cache_categories(self, categories):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # First execute: CREATE TABLE
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE CHECK(LENGTH(name) > 0),
                  size INTEGER CHECK(size > 0),
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            """
            AFTER UPDATE ON categories → Trigger fires when ANY row is UPDATED
            NEW.id refers to the ID of the row that was just updated
            WHERE id = NEW.id ensures we ONLY update the timestamp on THAT specific row
            """
            # Second execute: CREATE TRIGGER
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
                AFTER UPDATE ON categories
                BEGIN
                    UPDATE categories SET last_updated = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
                """
            )

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
          
          # FIRST: Check if table exists
          cursor.execute("""
              SELECT name FROM sqlite_master 
              WHERE type='table' AND name='categories'
          """)
          
          # Table missing - definitely need download
          if not cursor.fetchone():
              print("📦 Categories cache doesn't exist, got to runterladen meow!")
              return False  
              
          # NOW: Table exists, try to use it
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
                      print(f"📦 Cache is {days_old:.0f} days old - refreshing")
                      return False
                      
              return True
              
          except sqlite3.OperationalError:
              return False
            

    def get_cached_directories(self):
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, size FROM categories ORDER BY name")
            categories = {name: size for name, size in cursor.fetchall()}
            return categories
            
    def update_bbc_directories_cache(self):
        categories = self.download_bbc_categories()
        self.cache_categories(categories)
              
    def get_bbc_directories(self):
        
        if not self.check_categories_cache():
            self.update_bbc_directories_cache()
            
        categories = self.get_cached_directories()
            
        return categories
      
    def get_cached_json(self, filename):
        path = Path(self.json_cache)
        filepath = path / f"{filename}.json"
        data = json.loads(filepath.read_text())
        return data


if __name__ == "__main__":
    # print("✨ meow!")
    audiodb = AudioDatabase()

    func_name = sys.argv[1]
    args = sys.argv[2:]
    # print(func_name)

    if func_name == "get_bbc_categories":
        categories = audiodb.get_bbc_directories()
        # print("🖨️  Printing categories")
        for key, val in categories.items():
            print(f"{key} {val}")
    elif func_name == "get_category_sounds":
        sounds


# Path("text.txt").write_text('\n'.join(descriptions))


# audiodb.test()
