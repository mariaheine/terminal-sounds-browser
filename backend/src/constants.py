from pathlib import Path

APPNAME = "terminal-sound-browser"
VERSION = "0.1.0"

HEADERS = {
    f"User-Agent": "{APPNAME}/{VERSION} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# CACHE LOCATIONS
CACHE_DIR = Path.home() / ".cache" / APPNAME
SOUNDS_CACHE_DIR = CACHE_DIR / "sounds"
DATABASE_DIR = CACHE_DIR / "database"

# BBC CACHE
BBC_DATABASE = DATABASE_DIR / "bbc.db"
BBC_SOUNDS_CACHE_DIR = SOUNDS_CACHE_DIR / "bbc"

# CONFIG LOCATIONS
CONFIG_DIR = Path.home() / ".config" / APPNAME 

# LOGS
LOGS_DIR = CACHE_DIR / "logs"
LOG_FILE_NAME = "loggy.log"

# BBC API
BBC_URL_API = "https://sound-effects-api.bbcrewind.co.uk/api/sfx"
BBC_URL_MEDIA = "https://sound-effects-media.bbcrewind.co.uk"
BBC_MP3_ENDPOINT = "/mp3/"
BBC_WAV_ENDPOINT = "/zip/"
BBC_API_SEARCH_ENDPOINT = "/search"
BBC_API_CATEGORY_AGGREGATIONS_ENDPOINT = "/categoryAggregations"

# STUFF
MAX_CACHE_AGE_DAYS = 7

# TODO WHEN IS THIS GETTING CALLED
# TODO THIS WILL NEED TO GET CALLED AGAIN AFTER A CACHE-CLEAR METHOD
for dir_path in [
        CACHE_DIR, 
        LOGS_DIR, 
        SOUNDS_CACHE_DIR, 
        DATABASE_DIR,
        BBC_SOUNDS_CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
