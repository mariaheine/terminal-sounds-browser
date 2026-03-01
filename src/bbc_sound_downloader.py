import requests
import sqlite3
from pathlib import Path
from src.logger import Logger
from src.database import Database

class BBCSoundDownloader:
    def __init__(self, logger: Logger, cache_path: Path, db_path: Path, category: str):
        self.logger = logger
        self.sound_cache = self.init_sound_cache(cache_path, category) 
        self.bbc_url_media = "http://sound-effects-media.bbcrewind.co.uk/"
        self.bbc_mp3_endpoint = "mp3/"
        self.bbc_wav_endpoint = "zip/"

    def init_sound_cache(self, cache_path: Path, category: str):
        sound_cache = cache_path / "sounds" / "bbc" / category
        sound_cache.mkdir(parents=True, exist_ok=True)
        return sound_cache

    def download_preview_sound(self, sound_id: str):
        filename = f"{sound_id}.mp3"
        filepath = self.sound_cache / filename
        url = f"{self.bbc_url_media}{self.bbc_mp3_endpoint}{sound_id}.mp3"
        
        # TODO stream?
        response = requests.get(url, stream=True)
        response.raise_for_status() # TODO meow?

        if response.status_code == 200:
            with filepath.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return filepath
        else:
            self.logger.error(f"Download bbc preview sound failed, status code: {response.status_code}")
            return None

    # def _download_sound_with_status(self, sound_id: str):

