"""
A Dashboard TUI Tool
"""

from dashboard.themes.themes import ALL_THEMES

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer

from dashboard.widgets.calendar import CalendarPanel
from dashboard.widgets.greeting import Greeting
from dashboard.widgets.clock import Clock
from dashboard.widgets.weather import WeatherPanel


class Dashboard(App):
    CSS_PATH = "style/dashboard.tcss"

    THEMES = [t.name for t in ALL_THEMES] + ["nord"]

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_weather", "Refresh weather"),
        ("c", "cycle_theme", "Cycle Themes")
    ]

    def action_refresh_weather(self) -> None:
        self.query_one(WeatherPanel).load_weather()

    
    def action_cycle_theme(self) -> None:
        current_theme_index = self.THEMES.index(self.theme)
        current_theme_index = (current_theme_index + 1) % len(self.THEMES)
        self.theme = self.THEMES[current_theme_index]


    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Vertical(
            Greeting(),
            Horizontal(Clock(), WeatherPanel(), id="status-row"),
            CalendarPanel(id="calendar-panel"),
        )
    
    def on_mount(self) -> None:
        for t in ALL_THEMES:
            self.register_theme(t)
        self.theme = self.THEMES[0]

def main():
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main()