"""
Typed configuration for the dashboard.

`config.toml` is parsed once into frozen dataclasses. Every setting has a
default, so only the values you want to change need to be in the file.
Unknown keys and wrong types raise a `ConfigError` with a readable message
instead of failing later inside a widget.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from dataclasses import asdict

import tomlkit

from dashboard.paths import PROJECT_CONFIG_PATH, USER_CONFIG_PATH

CONFIG_ENV_VAR = "DASHBOARD_CONFIG"


class ConfigError(Exception):
    """Raised when the config file is missing or invalid."""


class ConfigNotFoundError(ConfigError):
    """Raised when no config file could be found."""


# --------------------------------------------------------------------------- #
# Config sections
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class CalendarSource:
    name: str
    url: str
    color: str | None = None
    enabled: bool = True


@dataclass(frozen=True)
class CalendarConfig:
    sources: tuple[CalendarSource, ...] = ()
    days_ahead: int = 7
    refresh_minutes: float = 10
    time_format: str = "%a %H:%M"

    @property
    def enabled_sources(self) -> tuple[CalendarSource, ...]:
        return tuple(s for s in self.sources if s.enabled)


@dataclass(frozen=True)
class WeatherConfig:
    lat: float = 59.9139
    lon: float = 10.7522
    refresh_minutes: float = 10


@dataclass(frozen=True)
class AppConfig:
    name: str = "there"
    theme: str = "norwegian-forest"
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    calendar: CalendarConfig = field(default_factory=CalendarConfig)
    path: Path | None = None  # where the config was loaded from


# --------------------------------------------------------------------------- #
# Locating the file
# --------------------------------------------------------------------------- #

def find_config_path(explicit: str | Path | None = None) -> Path:
    """
    Search order:
      1. an explicit path (e.g. from --config)
      2. $DASHBOARD_CONFIG
      3. $XDG_CONFIG_HOME/tui-dashboard/config.toml (~/.config/... by default)
      4. config.toml in the project root (for running from the repo)
    """
    if explicit is not None:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ConfigError(f"Config file not found: {path}")
        return path

    candidates: list[Path] = []
    if env := os.environ.get(CONFIG_ENV_VAR):
        candidates.append(Path(env).expanduser())
    candidates += [USER_CONFIG_PATH, PROJECT_CONFIG_PATH]

    for path in candidates:
        if path.is_file():
            return path

    searched = "\n".join(f"  - {p}" for p in candidates)
    raise ConfigNotFoundError(
        "No config file found. Looked in:\n"
        f"{searched}\n"
        f"Copy config.toml.example to {USER_CONFIG_PATH} and fill it in."
    )


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = find_config_path(path)
    try:
        with config_path.open("rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{config_path}: invalid TOML: {e}") from e

    try:
        return parse_config(raw, config_path)
    except ConfigError as e:
        raise ConfigError(f"{config_path}: {e}") from None


def parse_config(raw: dict[str, Any], path: Path | None = None) -> AppConfig:
    """Validate a TOML-shaped dict. Used by load_config and the setup screen."""
    return _parse_app(raw, path)

# --------------------------------------------------------------------------- #
# Creating the config file
# --------------------------------------------------------------------------- #

def config_to_dict(config: AppConfig) -> dict[str, Any]:
    """The reverse of parse_config. Drops None values, which TOML can't store."""
    def clean(d: dict) -> dict:
        return {k: v for k, v in d.items() if v is not None}

    c = config.calendar
    return {
        "name": config.name,
        "theme": config.theme,
        "weather": asdict(config.weather),
        "calendar": {
            "days_ahead": c.days_ahead,
            "refresh_minutes": c.refresh_minutes,
            "time_format": c.time_format,
            "sources": [clean(asdict(s)) for s in c.sources],
        },
    }

def save_config(config: AppConfig, path: Path = USER_CONFIG_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    # Create the file readable only by the user: it contains calendar links.
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(tomlkit.dumps(config_to_dict(config)))
    os.replace(tmp, path)  # all at once: no half-written config if the app dies
    return path

# --------------------------------------------------------------------------- #
# Parsing / validation
# --------------------------------------------------------------------------- #

def _parse_app(raw: dict[str, Any], path: Path) -> AppConfig:
    if "calendars" in raw:
        raise ConfigError(
            "[calendars] is the old format. Use [[calendar.sources]] entries "
            "instead (see config.toml.example)."
        )
    _reject_unknown(raw, {"name", "theme", "weather", "calendar"}, "top level")

    return AppConfig(
        name=_get(raw, "name", str, AppConfig.name, "top level"),
        theme=_get(raw, "theme", str, AppConfig.theme, "top level"),
        weather=_parse_weather(_get(raw, "weather", dict, {}, "top level")),
        calendar=_parse_calendar(_get(raw, "calendar", dict, {}, "top level")),
        path=path,
    )


def _parse_weather(raw: dict[str, Any]) -> WeatherConfig:
    where = "[weather]"
    _reject_unknown(raw, {"lat", "lon", "refresh_minutes"}, where)
    d = WeatherConfig()
    cfg = WeatherConfig(
        lat=_get(raw, "lat", float, d.lat, where),
        lon=_get(raw, "lon", float, d.lon, where),
        refresh_minutes=_get(raw, "refresh_minutes", float, d.refresh_minutes, where),
    )
    if not -90 <= cfg.lat <= 90:
        raise ConfigError(f"{where} lat must be between -90 and 90, got {cfg.lat}")
    if not -180 <= cfg.lon <= 180:
        raise ConfigError(f"{where} lon must be between -180 and 180, got {cfg.lon}")
    _require_positive(cfg.refresh_minutes, "refresh_minutes", where)
    return cfg


def _parse_calendar(raw: dict[str, Any]) -> CalendarConfig:
    where = "[calendar]"
    _reject_unknown(raw, {"days_ahead", "refresh_minutes", "time_format", "sources"}, where)
    d = CalendarConfig()

    raw_sources = _get(raw, "sources", list, [], where)
    sources = tuple(_parse_source(s, i) for i, s in enumerate(raw_sources, start=1))

    names = [s.name for s in sources]
    if dupes := sorted({n for n in names if names.count(n) > 1}):
        raise ConfigError(f"{where} duplicate calendar names: {', '.join(dupes)}")

    cfg = CalendarConfig(
        sources=sources,
        days_ahead=_get(raw, "days_ahead", int, d.days_ahead, where),
        refresh_minutes=_get(raw, "refresh_minutes", float, d.refresh_minutes, where),
        time_format=_get(raw, "time_format", str, d.time_format, where),
    )
    _require_positive(cfg.days_ahead, "days_ahead", where)
    _require_positive(cfg.refresh_minutes, "refresh_minutes", where)
    return cfg


def _parse_source(raw: Any, index: int) -> CalendarSource:
    where = f"[[calendar.sources]] #{index}"
    if not isinstance(raw, dict):
        raise ConfigError(f"{where} must be a table")
    _reject_unknown(raw, {"name", "url", "color", "enabled"}, where)

    name = _get(raw, "name", str, None, where, required=True)
    where = f'calendar source "{name}"'
    url = _normalize_url(_get(raw, "url", str, None, where, required=True), where)

    return CalendarSource(
        name=name,
        url=url,
        color=_get(raw, "color", str, None, where),
        enabled=_get(raw, "enabled", bool, True, where),
    )


def _normalize_url(url: str, where: str) -> str:
    url = url.strip()
    # Outlook and Google often hand out webcal:// links; they are plain HTTPS.
    if url.startswith("webcal://"):
        url = "https://" + url.removeprefix("webcal://")
    if not url.startswith(("https://", "http://")):
        raise ConfigError(f"{where} url must start with https:// or webcal://")
    if "..." in url:
        raise ConfigError(f"{where} url still contains the example placeholder")
    return url


_MISSING = object()


def _get(table: dict, key: str, typ: type, default: Any, where: str, *, required: bool = False) -> Any:
    value = table.get(key, _MISSING)
    if value is _MISSING:
        if required:
            raise ConfigError(f"{where} is missing required key '{key}'")
        return default

    # bool is a subclass of int in Python; don't let `true` pass as a number.
    if typ in (int, float) and isinstance(value, bool):
        ok = False
    elif typ is float:
        ok = isinstance(value, (int, float))
        value = float(value) if ok else value
    else:
        ok = isinstance(value, typ)

    if not ok:
        raise ConfigError(
            f"{where} '{key}' should be {_type_name(typ)}, got {_type_name(type(value))} ({value!r})"
        )
    return value


def _reject_unknown(table: dict, allowed: set[str], where: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ConfigError(
            f"{where} has unknown key(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(sorted(allowed))}"
        )


def _require_positive(value: float, key: str, where: str) -> None:
    if value <= 0:
        raise ConfigError(f"{where} '{key}' must be greater than 0, got {value}")


def _type_name(typ: type) -> str:
    return {
        str: "a string", int: "an integer", float: "a number", bool: "true/false",
        dict: "a table", list: "a list",
    }.get(typ, typ.__name__)
