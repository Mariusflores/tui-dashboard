"""
A Dashboard TUI Tool
"""

import argparse
import sys
from dataclasses import replace

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from dashboard.config import AppConfig, ConfigError, ConfigNotFoundError, load_config, save_config
from dashboard.screens.setup import SetupScreen
from dashboard.themes.themes import ALL_THEMES
from dashboard.widgets.base import RefreshingPanel
from dashboard.widgets.calendar import CalendarPanel
from dashboard.widgets.clock import Clock
from dashboard.widgets.greeting import Greeting
from dashboard.widgets.weather import WeatherPanel


class Dashboard(App):
    CSS_PATH = "style/dashboard.tcss"

    THEMES = [t.name for t in ALL_THEMES] + ["nord"]

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("c", "cycle_theme", "Cycle Themes"),
    ]

    def __init__(self, config: AppConfig | None) -> None:
        super().__init__()
        self.config = config

    # --- layout ------------------------------------------------------------ #

    def _main_layout(self) -> Vertical:
        return Vertical(
            Greeting(self.config.name),
            Horizontal(Clock(), WeatherPanel(self.config.weather), id="status-row"),
            CalendarPanel(self.config.calendar, id="calendar-panel"),
        )

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        if self.config is not None:
            yield self._main_layout()

    def on_mount(self) -> None:
        for t in ALL_THEMES:
            self.register_theme(t)

        if self.config is None:
            # Show setup on top; _setup_done runs when it calls dismiss(config)
            self.push_screen(SetupScreen(self.THEMES), callback=self._setup_done)
        else:
            self._apply_theme()

    def _setup_done(self, config: AppConfig | None) -> None:
        path = save_config(config)
        self.config = config
        self.mount(self._main_layout())  # add widgets to the now-visible main screen
        self._apply_theme()
        self.notify(f"Saved config to {path}")

    def _apply_theme(self) -> None:
        if self.config.theme in self.available_themes:
            self.theme = self.config.theme
        else:
            self.theme = self.THEMES[0]
            self.notify(
                f'Unknown theme "{self.config.theme}", using "{self.THEMES[0]}".',
                severity="warning",
            )

    # --- actions (key bindings) ------------------------------------------- #

    def action_refresh(self) -> None:
        for panel in self.query(RefreshingPanel):
            panel.reload()

    def action_cycle_theme(self) -> None:
        # The theme may have been picked from the command palette and not be in THEMES.
        index = self.THEMES.index(self.theme) if self.theme in self.THEMES else -1
        self.theme = self.THEMES[(index + 1) % len(self.THEMES)]
        self._save_theme()

    def _save_theme(self) -> None:
        if self.config is None:
            return
        self.config = replace(self.config, theme=self.theme)
        save_config(self.config, self.config.path)


def main():
    parser = argparse.ArgumentParser(prog="dashboard", description="A terminal dashboard.")
    parser.add_argument("-c", "--config", help="path to a config.toml file")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigNotFoundError:
        config = None  # -> setup screen
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    Dashboard(config).run()


if __name__ == "__main__":
    main()
