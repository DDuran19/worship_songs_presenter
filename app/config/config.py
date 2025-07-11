from typing import TypedDict
from pathlib import Path
import json

# ─── TypedDict Definitions ────────────────────────────────────────────────────
class PathsConfig(TypedDict):
    temp:   str  # where to write temporary files/logs
    lyrics: str  # where to read/write lyrics JSON
    videos: str  # where to read background videos

class AppConfig(TypedDict):
    name:    str  # application name
    version: str  # application version

class ConfigType(TypedDict):
    app:   AppConfig
    paths: PathsConfig


# ─── Project Paths ─────────────────────────────────────────────────────────────
# BASE_DIR   -> worship_songs_presenter/
# CONFIG_DIR -> worship_songs_presenter/config/
# DATA_DIR   -> worship_songs_presenter/data/
BASE_DIR   = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR   = BASE_DIR / "data"


# ─── Load Default Settings ─────────────────────────────────────────────────────
_defaults_path = CONFIG_DIR / "defaults.json"
with _defaults_path.open("r", encoding="utf-8") as f:
    _defaults = json.load(f)


# ─── Build the Config Dict ─────────────────────────────────────────────────────
config: ConfigType = {
    "app": {
        "name":    _defaults.get("app_name",    "Worship Songs Presenter"),
        "version": _defaults.get("version",     "0.1.0"),
    },
    "paths": {
        "temp":   str(DATA_DIR   / "temp"),
        "lyrics": str(DATA_DIR   / "lyrics"),
        "videos": str(BASE_DIR   / "videos"),
    },
}


# ─── Ensure Required Directories Exist ─────────────────────────────────────────
# so you don’t have to mkdir in your main code
Path(config["paths"]["temp"]).mkdir(parents=True, exist_ok=True)
Path(config["paths"]["lyrics"]).mkdir(parents=True, exist_ok=True)
# if you want to guarantee videos dir too:
Path(config["paths"]["videos"]).mkdir(parents=True, exist_ok=True)
