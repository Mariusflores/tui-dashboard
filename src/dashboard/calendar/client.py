import httpx
import tomllib
from pathlib import Path
from icalendar import Calendar
import recurring_ical_events
from datetime import date, timedelta
from dashboard.calendar.models import Event


def get_upcoming_events():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

    CONFIG_PATH = PROJECT_ROOT / "config.toml"
    with CONFIG_PATH.open("rb") as f:
        config = tomllib.load(f)

    google_url = config["calendars"]["google"]

    response = httpx.get(google_url)
    response.raise_for_status()
    ics_text = response.text

    cal = Calendar.from_ical(ics_text)
    
    today = date.today()
    events = recurring_ical_events.of(cal).between(today, today + timedelta(days=7))
    response = []
    for event in events:
        response.append(
            Event(summary=event.get("SUMMARY"), start=event.get("DTSTART").dt, end=event.get("DTEND").dt )
        )
    
    return response

