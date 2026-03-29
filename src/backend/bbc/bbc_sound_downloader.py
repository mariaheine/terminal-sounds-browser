import subprocess
import sys
from src.backend.common.logger import Logger
from src.backend.common.config_manager import ConfigManager
from src.backend.constants import (
    SOUNDS_CACHE_DIR,
    BBC_URL_MEDIA,
    BBC_MP3_ENDPOINT,
    BBC_WAV_ENDPOINT,
)

class BBCSoundDownloader:
    def __init__(self):
        self.logger = Logger()
        
    def download_preview_sound(self, category: str, sound_id: str):

        if not sound_id:
            self.logger.error("Called download_preview_sound for a null or empty sound_id.")
            return False

        if not category:
            self.logger.error("Called download_preview_sound for a null or empty category.")
            return False

        download_dir = SOUNDS_CACHE_DIR / "bbc" / category
        download_dir.mkdir(parents=True, exist_ok=True)
        file_path = download_dir / f"{sound_id}.mp3"
        url = f"{BBC_URL_MEDIA}{BBC_MP3_ENDPOINT}{sound_id}.mp3"

        subprocess.Popen([
            sys.executable, # TODO
            '-m',
            'src.backend.common.download_worker',
            url,
            file_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def download_favourite_wav(self, sound_id: str, filename: str):

        if not sound_id:
            self.logger.error("Called download_favourite_wav for a null or empty sound_id.")
            return False

        config = ConfigManager()
        dest_dir = config.get("downloads", "favourites_path")

        if not dest_dir:
            self.logger.error("Favourites download path is not configured.")
            return False

        url = f"{BBC_URL_MEDIA}{BBC_WAV_ENDPOINT}{sound_id}.wav.zip"

        subprocess.Popen([
            sys.executable,
            '-m',
            'src.backend.bbc.wav_download_worker',
            url,
            dest_dir,
            sound_id,
            filename,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
