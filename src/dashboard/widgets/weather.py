from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Static

from dashboard.config import WeatherConfig
from dashboard.weather.client import get_current_weather


class WeatherPanel(VerticalGroup):
    """ Weather Widget """

    def __init__(self, config: WeatherConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Static("", id="symbol")
        yield Static("", id="temp")

    def on_mount(self) -> None:
        self.load_weather()
        self.set_interval(self.config.refresh_minutes * 60, self.load_weather)

    @work(exclusive=True)
    async def load_weather(self) -> None:
        try:
            symbol, temp = await get_current_weather(self.config.lat, self.config.lon)
            self.query_one("#symbol", Static).update(symbol)
            self.query_one("#temp", Static).update(temp)
        except Exception:  # network errors, unexpected API responses
            self.query_one("#symbol", Static).update("Something went wrong: ⚠️")
            self.query_one("#temp", Static).update("")
