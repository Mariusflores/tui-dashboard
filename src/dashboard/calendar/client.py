import asyncio
from datetime import date, datetime, time, timedelta

import httpx
import recurring_ical_events
from icalendar import Calendar

from dashboard.calendar.models import Event
from dashboard.config import CalendarConfig, CalendarSource


async def get_upcoming_events(config: CalendarConfig) -> tuple[list[Event], list[str]]:
    """
    Fetch all enabled calendar sources concurrently.

    Returns (events sorted by start, error messages). A failing source is
    reported in the error list instead of hiding events from the others.
    """
    sources = config.enabled_sources
    start = date.today()
    end = start + timedelta(days=config.days_ahead)

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(_fetch_source(client, source, start, end) for source in sources),
            return_exceptions=True,
        )

    events: list[Event] = []
    errors: list[str] = []
    for source, result in zip(sources, results):
        if isinstance(result, BaseException):
            errors.append(f"{source.name}: {_describe_error(result)}")
        else:
            events.extend(result)

    return sorted(events, key=lambda e: e.start), errors


async def _fetch_source(
    client: httpx.AsyncClient, source: CalendarSource, start: date, end: date
) -> list[Event]:
    response = await client.get(source.url)
    response.raise_for_status()
    cal = Calendar.from_ical(response.text)

    events = []
    for component in recurring_ical_events.of(cal).between(start, end):
        raw_start = component.get("DTSTART").dt
        raw_end = component.get("DTEND").dt if component.get("DTEND") else raw_start
        events.append(
            Event(
                summary=str(component.get("SUMMARY", "(no title)")),
                start=_to_local(raw_start),
                end=_to_local(raw_end),
                all_day=not isinstance(raw_start, datetime),
                source=source.name,
                color=source.color,
            )
        )
    return events

async def test_source(source: CalendarSource, days_ahead: int = 7) -> int:
    """Fetch a single source and return how many events it has. Raises on failure."""
    start = date.today()
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        events = await _fetch_source(client, source, start, start +
        timedelta(days=days_ahead))
    return len(events)

def _to_local(value: date | datetime) -> datetime:
    """Turn dates, naive and aware datetimes into aware local datetimes so they sort together."""
    if not isinstance(value, datetime):
        value = datetime.combine(value, time.min)
    return value.astimezone()


def _describe_error(error: BaseException) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return f"HTTP {error.response.status_code}"
    if isinstance(error, httpx.HTTPError):
        return type(error).__name__
    return f"{type(error).__name__}: {error}"
