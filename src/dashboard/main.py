"""
An App to show the current time.
"""

from datetime import datetime
from dashboard.weather.client import fetch_data

from textual.app import App, ComposeResult
from textual.containers import VerticalGroup, HorizontalScroll, VerticalScroll, HorizontalGroup
from textual.widgets import Digits, Header, Static, Footer

class Clock(VerticalGroup):

    def compose(self) -> ComposeResult:
        yield Digits("")
    
    def on_mount(self) -> None:   
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


class WeatherPanel(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Static("", id="symbol")
        yield Static("", id="temp")


    def on_mount(self) -> None:
        self.fetch_data()

    def fetch_data(self) -> None:
        data = fetch_data()
        self.query_one("#symbol", Static).update(data[0])
        self.query_one("#temp", Static).update(data[1])

    

class Dashboard(App):
    CSS_PATH = "style/dashboard.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield HorizontalScroll(Clock(), WeatherPanel())
    
    def on_mount(self) -> None:
        self.theme = "atom-one-dark"

def main():
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main()