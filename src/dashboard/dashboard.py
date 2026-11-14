"""
A Dashboard TUI Tool
"""

import argparse
import sys

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from dashboard.config import AppConfig, ConfigError, load_config
from dashboard.themes.themes import ALL_THEMES
from dashboard.widgets.calendar import CalendarPanel
from dashboard.widgets.clock import Clock
from dashboard.widgets.greeting import Greeting
from dashboard.widgets.weather import WeatherPanel


class Dashboard(App):
    CSS_PATH = "style/dashboard.tcss"

    THEMES = [t.name for t in ALL_THEMES] + ["nord"]

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_weather", "Refresh weather"),
        ("c", "cycle_theme", "Cycle Themes"),
    ]

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config

    def action_refresh_weather(self) -> None:
        self.query_one(WeatherPanel).load_weather()

    def action_cycle_theme(self) -> None:
        # The theme may have been picked from the command palette and not be in THEMES.
        index = self.THEMES.index(self.theme) if self.theme in self.THEMES else -1
        self.theme = self.THEMES[(index + 1) % len(self.THEMES)]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Vertical(
            Greeting(self.config.name),
            Horizontal(Clock(), WeatherPanel(self.config.weather), id="status-row"),
            CalendarPanel(self.config.calendar, id="calendar-panel"),
        )

    def on_mount(self) -> None:
        for t in ALL_THEMES:
            self.register_theme(t)

        if self.config.theme in self.available_themes:
            self.theme = self.config.theme
        else:
            self.theme = self.THEMES[0]
            self.notify(
                f'Unknown theme "{self.config.theme}", using "{self.THEMES[0]}".',
                severity="warning",
            )


def main():
    parser = argparse.ArgumentParser(prog="dashboard", description="A terminal dashboard.")
    parser.add_argument("-c", "--config", help="path to a config.toml file")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    Dashboard(config).run()


if __name__ == "__main__":
    main()
