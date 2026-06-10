from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Digits, Static


from datetime import datetime


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