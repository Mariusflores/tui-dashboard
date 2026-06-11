import httpx
import tomllib
from pathlib import Path
from icalendar import Calendar
import recurring_ical_events
from datetime import date, timedelta, datetime, time, timezone
from dashboard.calendar.models import Event
from dashboard.config import CONFIG


async def get_upcoming_events():

    google_url = CONFIG["calendars"]["google"]

    async with httpx.AsyncClient() as client:
        response = await client.get(google_url)
        response.raise_for_status()
        ics_text = response.text
        cal = Calendar.from_ical(ics_text)
        today = date.today()
        events = recurring_ical_events.of(cal).between(today, today + timedelta(days=7))
        response = []
        for event in events:
            raw_start = event.get("DTSTART").dt
            all_day = not isinstance(raw_start, datetime)
            start = datetime.combine(raw_start, time.min, tzinfo=timezone.utc) if all_day else raw_start
            response.append(
                Event(summary=event.get("SUMMARY"), start=start, end=event.get("DTEND").dt, all_day=all_day )
            )
    
    return sorted(response, key=lambda e: e.start)

