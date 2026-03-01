from pathlib import Path

# LOCATIONS
CACHE_DIR = Path.home() / ".cache" / "terminal-effect-browser"
LOGS_DIR = CACHE_DIR / "logs"
SOUNDS_CACHE_DIR = CACHE_DIR / "sounds"
# CONFIG_DIR = Path.home() / ".config" / "terminal-effect-browser"

# BBC API
BBC_API_BASE = "https://sound-effects-api.bbcrewind.co.uk"
BBC_URL_MEDIA = "https://sound-effects-media.bbcrewind.co.uk"
BBC_MP3_ENDPOINT = "/mp3/"
BBC_WAV_ENDPOINT = "/zip/"

# STUFF
MAX_CACHE_AGE_DAYS = 7

# Verzeichnisse automatisch erstellen
for dir_path in [CACHE_DIR, LOGS_DIR, SOUNDS_CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
