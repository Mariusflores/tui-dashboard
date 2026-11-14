from textual.app import ComposeResult
from textual.widgets import Static

from dashboard.config import WeatherConfig
from dashboard.weather.client import WeatherDisplay, get_current_weather
from dashboard.widgets.base import RefreshingPanel


class WeatherPanel(RefreshingPanel[WeatherDisplay]):
    """Weather Widget"""

    def __init__(self, config: WeatherConfig, **kwargs) -> None:
        super().__init__(config.refresh_minutes, **kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Static("", id="symbol")
        yield Static("", id="temp")

    async def fetch(self) -> WeatherDisplay:
        return await get_current_weather(self.config.lat, self.config.lon)

    def show(self, data: WeatherDisplay) -> None:
        self.query_one("#symbol", Static).update(data.symbol_line)
        self.query_one("#temp", Static).update(data.temperature_line)

    def show_error(self, error: Exception) -> None:
        self.query_one("#symbol", Static).update("Couldn't load weather ⚠️")
        self.query_one("#temp", Static).update("")
