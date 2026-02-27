from sre_parse import CATEGORIES
import requests
import zipfile
import sqlite3
import json
from pathlib import Path
from src.logger import Logger

class BBCSounds:
    def __init__(self, logger: Logger, db_path: Path, category: str, size: int):
        self.db_path = db_path
        self.category = category
        self.size = size
        self.logger = logger
        self.bbc_url_api = "https://sound-effects-api.bbcrewind.co.uk/"
        self.bbc_url_media = "http://sound-effects-media.bbcrewind.co.uk/"
        self.sounds_search_endpoint = "api/sfx/search"
        self.mp3_endpoint = "mp3/"
        self.wav_endpoint = "zip/"
        self.headers = {
            f"User-Agent": "bbc-sound-browser/{version} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.logger.debug("meow")

    def download_sounds_data_for_category(self):
        payload = {
            "criteria": {
                "caregories": [ self.category ],
                "from": 0,
                "size": self.size,
            }
        }

        response = requests.post(
            f"{self.bbc_url_api}{self.sounds_search_endpoint}",
            json=payload,
            headers=self.headers,
        )

        if response.status_code == 200:
            data = response.json()
            
            # self.save_example_sound_json(data["results"][0])

            #structure of response body:
            #{
            #   "results": [
            #       {
            #           "id": "07123" ! it is the same as the mp3 filename !
            #           "description": "asdf"
            #           "categ
            #           "duration": 1234124.43
            #           there are also: tags, location, 
            #       }
            #   ]
            #}
 
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


            #sound_db = {
             #   key: value["id"] for key, value in data["results"]
            #}

            #self.download_sound(list(sound_db.keys())[0])

            return sound_db

            # return list(sound_db.items())[0]
        else:
            # TODO handle
            print("failed")
            sys.exit(1)

    # TODO move to some neat utils class
    def save_example_sound_json(self, json_obj):
        json_docs_path = Path('./docs') / 'json_responses'
        json_docs_path.mkdir(parents=True, exist_ok=True)
        json_path = json_docs_path / "example_bbc_sound.json"
        json_text = json.dumps(json_obj)
        json_path.write_text(json_text)


    def cache_sounds_data(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Table for individual bbc sound effect data
            # Id is taken from the original sound id, see example json
            # Tags are simply comma separated
            # If it will make sense to make them more query-able then remake as junction tables
            # TODO tags just removed for now
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sounds (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    duration REAL NOT NULL,
                    favourite BOOLEAN DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Junction Table
            # categories 2 sounds
            cursor.execute("""
               CREATE TABLE IF NOT EXISTS sound_categories (
                    sound_id TEXT NOT NULL,
                    category_id INTEGER NOT NULL,

                    PRIMARY KEY (sound_id, category_id),
                    FOREIGN KEY (sound_id) REFERENCES sounds(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
               )""")

            indexes = [
                # TODO wouldn't it be cleaner to make the cat title index where cat table is?
                "CREATE INDEX IF NOT EXISTS idx_categories_title ON categories(name)",
                "CREATE INDEX IF NOT EXISTS idx_sound_categories ON sound_categories(category_id)",
            ]

            for i in indexes:
                cursor.execute(i)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_sounds_timestamp 
                AFTER UPDATE ON sounds
                BEGIN
                    UPDATE sounds SET last_updated = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
                """)

            conn.commit()

            for sound_id, value in data.items():
                cursor.execute("""
                    INSERT OR REPLACE 
                    INTO sounds (id, description, duration)
                    VALUES(?,?,?)
                    """,
                     (sound_id, value["description"], value["duration"]))

                for category_name in value["categories"]:

                    cursor.execute("""
                        SELECT id FROM categories
                        WHERE name = ?
                        """, (category_name,))

                    row = cursor.fetchone()

                    if row is None:
                        # categories are handled in bcc categories script
                        # if cat for title was not found here
                        # it means a sample sound had an additional unlisted category in it 
                        # we are ignoring it 
                        continue

                    category_id = row[0]

                    cursor.execute("""
                        INSERT OR IGNORE INTO sound_categories (sound_id, category_id)
                        VALUES (?,?)
                        """, (sound_id, category_id))

                    conn.commit()

    def check_sounds_cache_for_category(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='sounds'
                """)

            if not cursor.fetchone():
                return False

            try:
                cursor.execute("""
                    SELECT COUNT(*), MAX(s.last_updated)
                    FROM sounds s
                    JOIN sound_categories sc ON sc.sound_id = s.id
                    JOIN categories c ON sc.category_id = c.id
                    WHERE c.name = ?
                """, (self.category,))
                
                #for row in cursor.fetchall():
                 #   self.logger.debug(row)

                count, last_updated = cursor.fetchone()

                if count == 0:
                    return False;

                self.logger.debug(f"Sounds length {count}")


                if last_updated:
                    cursor.execute("""
                        SELECT julianday('now') - julianday(?)
                    """, (last_updated,))
                    days_old = cursor.fetchone()[0]
                    
                    if days_old > 7:
                        self.logger.info(f"📦 Cache is {days_old:.0f} days old - refreshing")
                        return False

                    self.logger.info(f"Found bbc sounds cache for {self.category} category.")

                    return True
                else:
                    self.logger.warning(f"Category {self.category} has problems with last_updated in sounds table")

                return False;
            
            except sqlite3.OperationalError:
                return False

    def update_sounds_data(self):
        sound_db = self.download_sounds_data_for_category()
        self.cache_sounds_data(sound_db)

    def get_sounds_data(self, category):

        self.logger.info(f"Getting bbc sounds data for category {self.category}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT description
                FROM sounds s
                JOIN sound_categories sc ON sc.sound_id = s.id
                JOIN categories c ON sc.category_id = c.id
                WHERE c.name = ?
                """, (category,))

            results = cursor.fetchall()

            self.logger.debug(f"length:")


            for row in results:
                self.logger.debug(row[0])

            return results
                

    def download_sound(self, sound_id):


        save_dir = Path('./cache')
        save_dir.mkdir(parents=True, exist_ok=True) 
        save_path = save_dir / f"{sound_id}.zip"

        url = f"{self.bbc_url_media}{self.wav_endpoint}{sound_id}.wav.zip"

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

    def get_sounds(self):

        if not self.check_sounds_cache_for_category():
            self.update_sounds_data()

        self.get_sounds_data(self.category)

