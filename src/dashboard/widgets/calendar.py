from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.markup import escape
from textual.widgets import Static

from dashboard.calendar.client import get_upcoming_events
from dashboard.calendar.models import Event
from dashboard.config import CalendarConfig


class CalendarPanel(VerticalGroup):
    """ Upcoming events from all enabled calendar sources """

    def __init__(self, config: CalendarConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Static("", id="events")

    def on_mount(self) -> None:
        self.load_calendar()
        self.set_interval(self.config.refresh_minutes * 60, self.load_calendar)

    @work(exclusive=True)
    async def load_calendar(self) -> None:
        events_widget = self.query_one("#events", Static)

        if not self.config.enabled_sources:
            events_widget.update("No calendars configured. Add [[calendar.sources]] to config.toml.")
            return

        try:
            events, errors = await get_upcoming_events(self.config)
        except Exception as e:  # never let a refresh take down the app
            events, errors = [], [f"{type(e).__name__}: {e}"]

        show_source = len(self.config.enabled_sources) > 1
        lines = [self._format_event(e, show_source) for e in events]
        if not lines and not errors:
            lines = [f"No events in the next {self.config.days_ahead} days."]
        lines += [f"[$error]⚠ {escape(err)}[/]" for err in errors]

        events_widget.update("\n".join(lines))

    def _format_event(self, event: Event, show_source: bool) -> str:
        when = f"{event.start:%a} all day" if event.all_day else f"{event.start:{self.config.time_format}}"
        line = f"{when}  {escape(event.summary)}"
        if show_source:
            line += f"  [dim]({escape(event.source)})[/]"
        if event.color:
            line = f"[{event.color}]{line}[/]"
        return line
