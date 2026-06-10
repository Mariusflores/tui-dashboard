from dashboard.weather.client import get_current_weather


from httpx import HTTPError
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Static


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