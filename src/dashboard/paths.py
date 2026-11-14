import os
from pathlib import Path

APP_NAME = "tui-dashboard"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_CONFIG_PATH = PROJECT_ROOT / "config.toml"

USER_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / APP_NAME
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.toml"
