import requests
import sqlite3
import subprocess
import sys
from pathlib import Path
from src.logger import Logger
from src.database import Database
from src.constants import (
    CACHE_DIR,
    SOUNDS_CACHE_DIR,
    BBC_URL_MEDIA,
    BBC_MP3_ENDPOINT
)


class BBCSoundDownloader:
    def __init__(self, logger: Logger, category: str, sound_id: str):
        self.logger = logger
        self.category = category
        self.sound_id = sound_id
        # self.bbc_url_media = "http://sound-effects-media.bbcrewind.co.uk/"
        # self.bbc_mp3_endpoint = "mp3/"
        # self.bbc_wav_endpoint = "zip/"

    # def init_sound_cache(self, cache_path: Path, category: str):
    #     sound_cache = cache_path / "sounds" / "bbc" / category
    #     sound_cache.mkdir(parents=True, exist_ok=True)
    #     return sound_cache

    def download_preview_sound(self):
        download_dir = SOUNDS_CACHE_DIR / "bbc" / self.category
        download_dir.mkdir(parents=True, exist_ok=True)
        file_path = download_dir / f"{self.sound_id}.mp3"
        url = f"{BBC_URL_MEDIA}{BBC_MP3_ENDPOINT}{self.sound_id}.mp3"

        subprocess.Popen([
            sys.executable, # TODO
            '-m',
            'src.download_worker',
            url,
            file_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # self.logger.info(f"downloading {sound_id}")
        # thread =  threading.Thread(
        #     target=self._download_sound_with_status,
        #     args=(sound_id,),
        #     daemon=True
        # )
        # thread.start()

    # def _download_sound_with_status(self, sound_id: str):
    #     temp_file = self.sound_cache / f"{sound_id}.tmp"
    #     final_file = self.sound_cache / f"{sound_id}.mp3"
    #
    #     self.logger.info(f"thread for id: {sound_id}")
    #
    #     if temp_file.exists():
    #         temp_file.unlink() # TODO
    #
    #     url = f"{self.bbc_url_media}{self.bbc_mp3_endpoint}{sound_id}.mp3"
    #     
    #     # TODO stream?
    #     response = requests.get(url, stream=True)
    #     response.raise_for_status() # TODO meow?
    #
    #     try:
    #         if response.status_code == 200:
    #             with temp_file.open("wb") as f:
    #                 for chunk in response.iter_content(chunk_size=8192):
    #                     f.write(chunk)
    #
    #             self.logger.warning(f"done {sound_id}")
    #             temp_file.rename(final_file)
    #         else:
    #             self.logger.error(f"Download bbc preview sound failed, status code: {response.status_code}")
    #             return None
    #
    #     except Exception as e:
    #         self.logger.error(f"Error while downloading sound for id: {sound_id}, status code: {response.status_code}, error: {e}")
    #
