from pathlib import Path

VERSION = "0.1.0"

HEADERS = {
    f"User-Agent": "bbc-sound-browser/{VERSION} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# LOCATIONS
CACHE_DIR = Path.home() / ".cache" / "terminal-effect-browser"
LOGS_DIR = CACHE_DIR / "logs"
SOUNDS_CACHE_DIR = CACHE_DIR / "sounds"
# CONFIG_DIR = Path.home() / ".config" / "terminal-effect-browser"

# BBC API
BBC_URL_API = "https://sound-effects-api.bbcrewind.co.uk/api/sfx"
BBC_URL_MEDIA = "https://sound-effects-media.bbcrewind.co.uk"
BBC_MP3_ENDPOINT = "/mp3/"
BBC_WAV_ENDPOINT = "/zip/"
BBC_API_SEARCH_ENDPOINT = "/search"
BBC_API_CATEGORY_AGGREGATIONS_ENDPOINT = "/categoryAggregations"

# STUFF
MAX_CACHE_AGE_DAYS = 7

# Verzeichnisse automatisch erstellen
for dir_path in [CACHE_DIR, LOGS_DIR, SOUNDS_CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
