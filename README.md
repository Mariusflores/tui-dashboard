# tui-dashboard

A personal terminal dashboard built with [Textual](https://textual.textualize.io/).
It greets you, shows the time and current weather, and lists upcoming events from
one or more calendars, all in one terminal window.

```
┌──────────────────────────────────────────────────────────┐
│                 Good Morning, Your Name!                 │
├────────────────────────────┬─────────────────────────────┤
│ Saturday, November 14, 2026│ Partlycloudy Day ⛅          │
│        08:42:17            │ 4.2°C                       │
├────────────────────────────┴─────────────────────────────┤
│ Sat 09:00  Standup  (Work)                               │
│ Sat all day  Birthday  (Personal)                        │
│ Mon 13:30  Dentist  (Personal)                           │
└──────────────────────────────────────────────────────────┘
```

## Features

- **Greeting** that changes with the time of day.
- **Clock** with a large digital display and the full date.
- **Weather** for any location, from the Norwegian Meteorological Institute's
  [Locationforecast API](https://api.met.no/weatherapi/locationforecast/2.0/documentation)
  (no API key needed).
- **Calendar** with upcoming events from any number of ICS feeds (Outlook, Google
  Calendar, iCloud, …), fetched concurrently. Recurring events are expanded, and
  each calendar can have its own color.
- **Resilient refreshes**: panels refresh on a timer in the background. If a
  refresh fails, the last good data stays on screen and is marked as stale. A
  broken calendar shows an error line without hiding events from the others.
- **Themes**: `norwegian-forest`, `graphite`, `hearth` and Textual's `nord`.
- **First-run setup screen**: if no config file exists, the app opens a form
  where you can pick a theme (with live preview), set your location, test a
  calendar link, and save.
- **Strict config validation**: typos, unknown keys and wrong types are reported
  with clear messages at startup instead of failing inside a widget later.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A terminal with Unicode and emoji support for the weather icons

## Installation

```sh
git clone https://github.com/Mariusflores/tui-dashboard.git
cd tui-dashboard
uv sync
```

Then run it with:

```sh
uv run dashboard
```

To install it as a standalone command available everywhere:

```sh
uv tool install .
dashboard
```

## Configuration

On first launch without a config file, the setup screen walks you through the
basics and saves the result to `~/.config/tui-dashboard/config.toml`. The file is
created with `0600` permissions, since calendar links grant read access to your
calendar.

For full control, copy the example and edit it:

```sh
mkdir -p ~/.config/tui-dashboard
cp config.toml.example ~/.config/tui-dashboard/config.toml
```

### Where the config is loaded from

The first file found wins:

1. The path given with `--config` / `-c`
2. `$DASHBOARD_CONFIG`
3. `$XDG_CONFIG_HOME/tui-dashboard/config.toml` (default `~/.config/tui-dashboard/config.toml`)
4. `config.toml` in the project root (handy when running from the repo; it's git-ignored)

### Options

Every setting is optional and falls back to the defaults below. The only
required values are `name` and `url` for each calendar source you add.

```toml
name = "Your Name"            # used in the greeting (default: "there")
theme = "norwegian-forest"    # norwegian-forest, graphite, hearth, nord

[weather]
lat = 59.9139                 # -90..90 (default: Oslo)
lon = 10.7522                 # -180..180
refresh_minutes = 10

[calendar]
days_ahead = 7                # how far ahead to list events
refresh_minutes = 10
time_format = "%a %H:%M"      # strftime format for event times

[[calendar.sources]]
name = "Work"                 # must be unique
url = "https://outlook.office365.com/owa/calendar/.../calendar.ics"
color = "$accent"             # optional: "red", "#7FB069" or a theme variable
enabled = true                # optional: set false to hide without deleting

[[calendar.sources]]
name = "Personal"
url = "webcal://..."          # webcal:// links are converted to https://
color = "$secondary"
```

When more than one calendar is enabled, each event shows which calendar it
came from.

### Getting an ICS link

- **Google Calendar:** Settings → *My Calendar* → Calendar settings →
  Scroll down and copy *Secret address in iCal format*.
- **Outlook / Microsoft 365:** Settings → Calendar → Shared calendars →
  *Publish a calendar* → copy the ICS link.

Treat these links like passwords: anyone with the link can read the calendar.

## Usage

```sh
uv run dashboard              # From repo folder
dashboard                     # uses the config search order above
dashboard -c path/to/config.toml
```

| Key      | Action                             |
| -------- | ---------------------------------- |
| `r`      | Refresh weather and calendar now   |
| `c`      | Cycle through themes               |
| `ctrl+p` | Command palette (Textual built-in) |
| `q`      | Quit                               |

## Project structure

```
src/dashboard/
├── dashboard.py          # App, key bindings and CLI entry point (main)
├── config.py             # Config loading, validation and saving
├── paths.py              # Config file locations
├── calendar/
│   ├── client.py         # Fetches and parses ICS feeds
│   └── models.py         # Event dataclass
├── weather/
│   ├── client.py         # met.no API client
│   └── symbols.py        # met.no symbol codes → emoji
├── screens/
│   └── setup.py          # First-run setup screen
├── widgets/
│   ├── base.py           # RefreshingPanel: timed background refresh + error handling
│   ├── calendar.py
│   ├── clock.py
│   ├── greeting.py
│   └── weather.py
├── themes/themes.py      # Custom Textual themes
└── style/dashboard.tcss  # Layout and styling
```

### Adding a panel

Panels that load data on a timer subclass `RefreshingPanel` and implement
`fetch()` (async, may raise), `show(data)` and optionally `show_error(error)`.
The base class handles the timer, the background worker, the `r` refresh key
and stale-data marking.

## Development

Run with Textual's dev tools for live CSS reloading and a debug console:

```sh
uv run textual console        # in one terminal
uv run textual run --dev src/dashboard/dashboard.py   # in another
```

## License

[MIT](LICENSE)
