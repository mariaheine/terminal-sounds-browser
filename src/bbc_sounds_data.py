from sre_parse import CATEGORIES
import requests
import zipfile
import sqlite3
import json
from pathlib import Path
from typing import Dict
from src.logger import Logger
from src.database import Database
from src.constants import HEADERS, BBC_DATABASE, BBC_URL_API, BBC_API_SEARCH_ENDPOINT

class BBCSounds:
    def __init__(self):
        self.db_path = BBC_DATABASE
        self.logger = Logger()
        self.database = Database(BBC_DATABASE, verbose=True)
        self.bbc_url_api = "https://sound-effects-api.bbcrewind.co.uk/"
        self.bbc_sounds_search_endpoint = "api/sfx/search"



    def download_sounds_data(self, category: str, category_size: int):

        self.logger.info(f"Downloading BBC sounds info for category {category} of size {category_size}")

        payload = {
            "criteria": {
                "categories": [ category ],
                "from": 0,
                "size": category_size,
            }
        }

        response = requests.post(
            f"{BBC_URL_API}{BBC_API_SEARCH_ENDPOINT}",
            json=payload,
            headers=HEADERS,
        )

        if response.status_code == 200:
            data = response.json()
            
            # To view the json response body structure from bbc
            # You can find this file neatly formatted in project doc files.
            # If it is outdated uncomment this to check new json out:
            # self.save_example_sound_json(data["results"][0])

            sound_db = {
                item["id"]: {
                    "description": item["description"],
                    "categories": [item["className"] for item in item["categories"]],
                    "duration": item["duration"],
                    "mp3_filename": item["file"]["small"]["name"],
                    "wav_filename": item["file"]["original"]["name"],
                    "tags": [tag.lower() for tag in item["tags"]]
                    }
                for item in data["results"]
            }

            self.logger.info(f"Downloaded {len(sound_db.keys())} sound descriptors from BBC.")

            return sound_db

        else:
            # TODO handle
            self.logger.error(f"Failed to get sounds data for category {category}, status code: {response.status_code}")
            # sys.exit(1)

    # TODO move to some neat utils class
    def save_example_sound_json(self, json_obj):
        json_docs_path = Path('./docs') / 'json_responses'
        json_docs_path.mkdir(parents=True, exist_ok=True)
        json_path = json_docs_path / "example_bbc_sound.json"
        json_text = json.dumps(json_obj)
        json_path.write_text(json_text)


    def cache_sounds_data(self, category: str, data):

        if category == "":
            self.logger.error("Empty category name, can't download sounds data.")
            return None

        self.logger.info(f"Caching BBC sounds info for category {category}")

        # Table for individual bbc sound effect data
        # Id is taken from the original sound id, see example json
        # Tags are simply comma separated
        # If it will make sense to make them more query-able then remake as junction tables
        # TODO tags just removed for now
        query = """
            CREATE TABLE IF NOT EXISTS sounds (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                duration REAL NOT NULL,
                favourite BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.database.execute(query)

        # Junction Table
        # categories 2 sounds
        query = """
           CREATE TABLE IF NOT EXISTS sound_categories (
                sound_id TEXT NOT NULL,
                category_id INTEGER NOT NULL,

                PRIMARY KEY (sound_id, category_id),
                FOREIGN KEY (sound_id) REFERENCES sounds(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
           )
        """
        self.database.execute(query)

        indexes = [
            # TODO wouldn't it be cleaner to make the cat title index where cat table is?
            "CREATE INDEX IF NOT EXISTS idx_categories_title ON categories(name)",
            "CREATE INDEX IF NOT EXISTS idx_sound_categories ON sound_categories(category_id)",
        ]

        for i in indexes:
            self.database.execute(i)
        
        query = """
            CREATE TRIGGER IF NOT EXISTS update_sounds_timestamp 
            AFTER UPDATE ON sounds
            BEGIN
                UPDATE sounds SET last_updated = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END;
            """
        self.database.execute(query)
        self.database.commit()

        if not data:
            self.logger.error("Can't cache missing sounds data, why did that happen?")

        for key, value in data.items():
            sound_id = key
            query = """
                INSERT OR REPLACE 
                INTO sounds (id, description, duration)
                VALUES(?,?,?)
                """
            params = (sound_id, value["description"], value["duration"])
            self.database.execute(query, params, silent=True)
            self.database.commit()

            for category_name in value["categories"]:

                query = """
                    SELECT id FROM categories
                    WHERE name = ?
                    """
                params = (category_name,)
                cursor = self.database.execute(query, params, silent=True)

                row = cursor.fetchone()
                # self.logger.warning(f"{category_name} {row}")

                if row is None:
                    # categories are handled in bcc categories script
                    # if cat for title was not found here
                    # it means a sample sound had an additional unlisted category in it 
                    # we are ignoring it
                    self.logger.warning(f"Inexisting category for name: {category_name}")
                    continue

                category_id = row[0]

                query = """
                    INSERT OR IGNORE INTO sound_categories (sound_id, category_id)
                    VALUES (?,?)
                    """
                params = (sound_id, category_id)
                self.database.execute(query, params, silent=True)
                self.database.commit()

    def check_sounds_cache_for_category(self, category: str, category_size: int):
        
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='sounds'
            """

        cursor = self.database.execute(query)

        if not cursor.fetchone():
            self.logger.info("Didn't find 'sounds' table in bbc db.")
            return False

        try:
            query = """
                SELECT COUNT(*), MAX(s.last_updated)
                FROM sounds s
                JOIN sound_categories sc ON sc.sound_id = s.id
                JOIN categories c ON sc.category_id = c.id
                WHERE c.name = ?
            """
            params = (category,)
            cursor = self.database.execute(query, params)
            
            # for row in cursor.fetchall():
            #    self.logger.debug(row)

            count, last_updated = cursor.fetchone()

            if count == 0:
                self.logger.info(f"BBC 'sounds' table was empty for category {category}")
                return False;

            if count != category_size:
                self.logger.info(f"BBC sounds category {category} size changed from {count} to {category_size}.")
                return False;

            if last_updated:
                query = """
                    SELECT julianday('now') - julianday(?)
                """
                params = (last_updated,)
                cursor = self.database.execute(query, params)

                days_old = cursor.fetchone()[0]
                
                if days_old > 7:
                    self.logger.info(f"📦 Cache is {days_old:.0f} days old - refreshing")
                    return False

                self.logger.info(f"Found bbc sounds cache for {category} category.")

                return True
            else:
                self.logger.error(f"Category {category} has problems with last_updated in sounds table")
                return False;
        
        except sqlite3.OperationalError:
            self.logger.error("sqlite operational error in check_sounds_cache_for_category")
            return False

    def update_sounds_data(self, category: str, category_size: int):
        sound_db = self.download_sounds_data(category, category_size)
        self.cache_sounds_data(category, sound_db)

    def get_sounds_data(self, category: str, category_size: int):

        self.logger.info(f"Getting bbc sounds data for category {category}")
        
        if not self.check_sounds_cache_for_category(category, category_size):
            self.update_sounds_data(category, category_size)

        query = "SELECT id, name FROM categories WHERE name = ?"
        params = (category,)
        cursor = self.database.execute(query,params)

        query = """
            SELECT s.id, s.description, s.duration, s.favourite
            FROM sounds s
            JOIN sound_categories sc ON sc.sound_id = s.id
            JOIN categories c ON sc.category_id = c.id
            WHERE c.name = ?
            """
        params = (category,)

        cursor = self.database.execute(query, params)

        sounds_data = cursor.fetchall()

        return sounds_data
                

    def download_sound(self, sound_id):


        save_dir = Path('./cache')
        save_dir.mkdir(parents=True, exist_ok=True) 
        save_path = save_dir / f"{sound_id}.zip"

        url = f"{self.bbc_url_media}{self.bbc_wav_endpoint}{sound_id}.wav.zip"

        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for errors

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        zip_path = save_path

        extract_path = zip_path.parent / zip_path.stem

        extract_path = Path(extract_path)
        extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        print(f"✅ Downloaded to {save_path}")


    def get_printable_sounds_data(self, category: str, category_size: int):
        """Returns a printable array of sounds, delimiter is '|' sign."""
        category_size = int(category_size)
        sounds_data = self.get_sounds_data(category, category_size)
        list_of_sounds = []
        for row in sounds_data:
            sound_id = row[0]
            sound_description: str = row[1]
            sound_duration = row[2]
            sound_favourite = row[3]

            if sound_favourite == 1:
                favourite_emoji = "⭐ "
            else:
                favourite_emoji = ""

            is_favourite = sound_favourite == 1

            list_of_sounds.append(f"{sound_id}|{sound_description}|{sound_duration}|{is_favourite}|{favourite_emoji}")
        # list_of_sounds = [f"{row[0]}|{row[1]}|{row[2]}" for row in sounds_data]
        return list_of_sounds

    def toggle_favourite(self, sound_id):
        query = """
            SELECT favourite
            FROM sounds
            WHERE id = ?
        """
        params = (sound_id,)
        cursor = self.database.execute(query, params)

        result = cursor.fetchone()
        if result is None:
            self.logger.warning(f"Can't toggle favourite on an unknown sound with id {sound_id}")
            return False

        # umschalten 1-0 0-1
        new_value = 1 - result[0]

        self.logger.debug(f"Setting {sound_id} to {new_value}")

        query = """
            UPDATE sounds
            SET favourite = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (new_value, sound_id)
        self.database.execute(query, params)
        self.database.commit()
        return True

    def set_favourite(self, value: bool, sound_id: str):
        query = """
            SELECT favourite
            FROM sounds
            WHERE id = ?
        """
        params = (sound_id,)
        cursor = self.database.execute(query, params)
        self.logger.debug(f"setttin fav {value} foor {sound_id} is {value == True}")

        result = cursor.fetchone()
        if result is None:
            self.logger.warning(f"Can't toggle favourite on an unknown sound with id {sound_id}")
            return False

        query = """
            UPDATE sounds
            SET favourite = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (value, sound_id)
        self.database.execute(query, params)
        self.database.commit()
        return True

    def is_favourite(self, sound_id):
        query = """
            SELECT favourite
            FROM sounds
            WHERE ID = ?
        """
        params = (sound_id,)
        cursor = self.database.execute(query, params)

        result = cursor.fetchone()
        if result is None:
            self.logger.warning(f"Can't check favourite status for an unknown sound at id: {sound_id}")
            return False

        is_favourite = result[0]

        return is_favourite == 1



