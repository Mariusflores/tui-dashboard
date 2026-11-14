"""
Base class for panels that fetch data on a timer.

Subclasses implement:
    fetch()            -> await and return the data (may raise)
    show(data)         -> render the data
    show_error(error)  -> optional; render an error when there is no data yet

The base class owns the timer, the background worker and error handling, so
a failed fetch never takes down the app. If a refresh fails after a
successful one, the old data stays on screen and the border subtitle marks
it as stale.
"""

from datetime import datetime

from textual import work
from textual.containers import VerticalGroup


class RefreshingPanel[T](VerticalGroup):

    def __init__(self, refresh_minutes: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.refresh_minutes = refresh_minutes
        self.last_updated: datetime | None = None

    # --- lifecycle --------------------------------------------------------- #

    def on_mount(self) -> None:
        self.reload()
        self.set_interval(self.refresh_minutes * 60, self.reload)

    @work(exclusive=True)
    async def reload(self) -> None:
        """Fetch and show new data. A new call cancels one that is still running."""
        try:
            data = await self.fetch()
        except Exception as error:
            self.log.error(f"{type(self).__name__} refresh failed: {error!r}")
            self._handle_error(error)
            return

        self.last_updated = datetime.now()
        self.border_subtitle = ""
        self.show(data)

    def _handle_error(self, error: Exception) -> None:
        if self.last_updated is None:
            self.border_subtitle = "⚠ refresh failed"
            self.show_error(error)
        else:
            self.border_subtitle = f"⚠ stale · last update {self.last_updated:%H:%M}"

    # --- implemented by subclasses ----------------------------------------- #

    async def fetch(self) -> T:
        raise NotImplementedError

    def show(self, data: T) -> None:
        raise NotImplementedError

    def show_error(self, error: Exception) -> None:
        """Called when a fetch fails before any data has been shown."""
