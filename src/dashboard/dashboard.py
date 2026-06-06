"""
A Dashboard TUI Tool
"""

from datetime import datetime
from httpx import HTTPError
from dashboard.weather.client import get_current_weather
from dashboard.calendar.client import get_upcoming_events
from dashboard.themes.themes import norwegian_forest 

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalGroup, Horizontal, Vertical
from textual.widgets import Digits, Header, Static, Footer


class Clock(VerticalGroup):
    """ Clock Widget """

    def compose(self) -> ComposeResult:
        yield Static("", id="date")
        yield Digits("", id="time")
    
    def on_mount(self) -> None:   
        self.update_clock()
        self.update_date()
        self.set_interval(1, self.update_clock)
        self.set_interval(60, self.update_date)
        


    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")

    def update_date(self):
        now = datetime.now()
        formatted = now.strftime("%A, %B %d, %Y")
        self.query_one(Static).update(formatted)


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

class CalendarPanel(VerticalGroup):
    
    def compose(self) -> ComposeResult:
        yield Static("", id="events")

    def on_mount(self) -> None:
        self.load_calendar()
        self.set_interval(600, self.load_calendar)

    @work(exclusive=True)
    async def load_calendar(self) -> None:
        events = await get_upcoming_events()
        lines = [f"{e.start:%a %H:%M}  {e.summary}" for e in events]
        text = "\n".join(lines)
        self.query_one("#events", Static).update(text)


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
        yield Vertical(
            Horizontal(Clock(), WeatherPanel(), id="status-row"),
            CalendarPanel(id="calendar-panel"),
        )
    
    def on_mount(self) -> None:
        self.register_theme(norwegian_forest)
        self.theme = "norwegian-forest"

def main():
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main()