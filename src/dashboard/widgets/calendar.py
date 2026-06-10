from dashboard.calendar.client import get_upcoming_events


from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Static


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