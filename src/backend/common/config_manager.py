import tomllib
from pathlib import Path
from src.backend.common.logger import Logger
from src.backend.constants import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULTS = {
    "downloads": {
        "favourites_path": None,
    }
}


class ConfigManager:
    def __init__(self):
        self.logger = Logger()
        self.config_file = CONFIG_FILE
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def is_initialized(self) -> bool:
        if not self.config_file.exists():
            return False
        config = self._read()
        return bool(config.get("downloads", {}).get("favourites_path"))

    def get(self, section: str, key: str) -> str | None:
        config = self._read()
        return config.get(section, {}).get(key)

    def set_favourites_path(self, path: str):
        resolved = str(Path(path).expanduser().resolve())
        Path(resolved).mkdir(parents=True, exist_ok=True)
        self._write({"downloads": {"favourites_path": resolved}})
        self.logger.info(f"Favourites download path set to: {resolved}")

    def _read(self) -> dict:
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            self.logger.error(f"Failed to read config: {e}")
            return {}

    def _write(self, data: dict):
        lines = []
        for section, values in data.items():
            lines.append(f"[{section}]")
            for key, value in values.items():
                lines.append(f'{key} = "{value}"')
            lines.append("")
        try:
            self.config_file.write_text("\n".join(lines))
        except Exception as e:
            self.logger.error(f"Failed to write config: {e}")
