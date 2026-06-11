import tomllib
from dashboard.paths import CONFIG_PATH


with CONFIG_PATH.open("rb") as f:
    CONFIG = tomllib.load(f)