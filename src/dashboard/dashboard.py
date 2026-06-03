"""
A Dashboard TUI Tool
"""

from datetime import datetime
from httpx import HTTPError
from dashboard.weather.client import get_current_weather

from textual import work
from textual.theme import Theme
from textual.app import App, ComposeResult
from textual.containers import VerticalGroup, Horizontal
from textual.widgets import Digits, Header, Static, Footer

norwegian_forest = Theme(
    name="norwegian-forest",
    primary="#6B8E5A",
    secondary="#4A7C59",
    accent="#C9A961",
    foreground="#D7CFA8",
    background="#0F1611",
    success="#7FB069",
    warning="#D4A574",
    error="#B8634E",
    surface="#16201A",
    panel="#1B2620",
    dark=True,
    variables={
        "boost": "#243029",
        "foreground-muted": "#8B9080",
        "border": "#3A4A3F",
    },
)

class Clock(VerticalGroup):
    """ Clock Widget """

    def compose(self) -> ComposeResult:
        yield Digits("")
    
    def on_mount(self) -> None:   
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


class WeatherPanel(VerticalGroup):
    """ Weather Widget """

    def compose(self) -> ComposeResult:
        yield Static("", id="symbol")
        yield Static("", id="temp")


    def on_mount(self) -> None:
        self.load_weather()
        self.set_interval(600, self.load_weather)

    @work(exclusive=True)
    async def load_weather(self) -> None:
        try:
            symbol, temp = await get_current_weather()
            self.query_one("#symbol", Static).update(symbol)
            self.query_one("#temp", Static).update(temp)
        except HTTPError:
            self.query_one("#symbol", Static).update("Something went wrong: ⚠️")
            self.query_one("#temp", Static).update("")


class Dashboard(App):
    CSS_PATH = "style/dashboard.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_weather", "Refresh weather"),
    ]

    def action_refresh_weather(self) -> None:
        self.query_one(WeatherPanel).load_weather()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Horizontal(Clock(), WeatherPanel())
    
    def on_mount(self) -> None:
        self.register_theme(norwegian_forest)
        self.theme = "norwegian-forest"

def main():
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main()