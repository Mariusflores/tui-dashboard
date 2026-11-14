from textual.app import ComposeResult
from textual.markup import escape
from textual.widgets import Static

from dashboard.calendar.client import get_upcoming_events
from dashboard.calendar.models import Event
from dashboard.config import CalendarConfig
from dashboard.widgets.base import RefreshingPanel

type CalendarData = tuple[list[Event], list[str]]  # (events, per-source errors)


class CalendarPanel(RefreshingPanel[CalendarData]):
    """Upcoming events from all enabled calendar sources"""

    def __init__(self, config: CalendarConfig, **kwargs) -> None:
        super().__init__(config.refresh_minutes, **kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Static("", id="events")

    async def fetch(self) -> CalendarData:
        if not self.config.enabled_sources:
            return [], []
        return await get_upcoming_events(self.config)

    def show(self, data: CalendarData) -> None:
        events, errors = data

        if not self.config.enabled_sources:
            self._set_text("No calendars configured. Add [[calendar.sources]] to config.toml.")
            return

        show_source = len(self.config.enabled_sources) > 1
        lines = [self._format_event(e, show_source) for e in events]
        if not lines and not errors:
            lines = [f"No events in the next {self.config.days_ahead} days."]
        lines += [f"[$error]⚠ {escape(err)}[/]" for err in errors]

        self._set_text("\n".join(lines))

    def show_error(self, error: Exception) -> None:
        self._set_text(f"[$error]⚠ Couldn't load calendars: {escape(str(error))}[/]")

    def _set_text(self, text: str) -> None:
        self.query_one("#events", Static).update(text)

    def _format_event(self, event: Event, show_source: bool) -> str:
        when = (
            f"{event.start:%a} all day"
            if event.all_day
            else f"{event.start:{self.config.time_format}}"
        )
        line = f"{when}  {escape(event.summary)}"
        if show_source:
            line += f"  [dim]({escape(event.source)})[/]"
        if event.color:
            line = f"[{event.color}]{line}[/]"
        return line
