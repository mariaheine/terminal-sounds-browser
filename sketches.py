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
import sqlite3
import time
import json
import subprocess
from pathlib import Path

version = "0.1.0"

class AudioDatabase:
    def __init__(self):
        self.db_path = "data/audio.db"
        self.request_delay = 0.5
        self.json_cache = "cache/json"
        self.sound_cache = "cache/sound"
        self.base_search_url = (
            "https://sound-effects-api.bbcrewind.co.uk/api/sfx/search"
        )
        self.headers = {
            f"User-Agent": "bbc-sound-browser/{version} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.categories = ["Aircraft", "Rain", "Thunder", "Traffic", "Birds"]
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

    def test(self):
        # response = self.session.get(f"{base_url}/Birds")
        # if response.status_code == 200:
        #     data = response.json()
        #     sound_descriptions = [sound['description'] for sound in data['results']]
        #     for des in sound_descriptions:
        #       print(des)
        # else:
        #     return None

        payload = {
            "criteria": {
                "from": 0,
                "size": 40,
                "tags": None,
                "categories": ["Animals"],
                "durations": None,
                "continents": None,
                "sortBy": None,
                "source": None,
                "recordist": None,
                "habitat": None,
            }
        }

        response = requests.post(base_url, json=payload, headers=headers)
        json = response.json()
        self.cache_json(json, "test")

    def cache_json(self, data, filename):
        path = Path(self.cache_json)
        path.mkdir(parents=True, exist_ok=True)
        
        filepath = path / f"{filename}.json"
        
        if isinstance(data, bytes):
            data = json.loads(data.decode('utf-8'))
        elif isinstance(data, str):
            data = json.loads(data)
        # if data was already a parsed json then lets just continue

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_cached_json(self, filename):
        path = Path(self.json_cache)
        filepath = path / f"{filename}.json"
        data = json.loads(filepath.read_text())
        return data
      
if __name__ == "__main__":
  print("✨ meow!")
  audiodb = AudioDatabase()
  data = audiodb.get_cached_json("test")
  print("⛈️ Total entries: " + str(data["total"]))
  descriptions = [val['description'] for val in data['results']]
  for desc in descriptions:
    print(desc)
  
  
# Path("text.txt").write_text('\n'.join(descriptions))


# audiodb.test()
