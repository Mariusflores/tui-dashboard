import asyncio
from typing import Any

from textual.app import ComposeResult
from textual.widgets import Static

from dashboard.sysutils.client import SystemInfo, get_system_info
from dashboard.widgets.base import RefreshingPanel

BAR_WIDTH = 10
GB = 1024**3


class SystemInfoPanel(RefreshingPanel[SystemInfo]):
    """CPU, memory and disk usage as colored bars."""

    def __init__(self, refresh_seconds: float = 5, **kwargs: Any) -> None:
        super().__init__(refresh_minutes=refresh_seconds / 60, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("", id="cpu")
        yield Static("", id="memory")
        yield Static("", id="disk")

    async def fetch(self) -> SystemInfo:
        # psutil blocks while sampling CPU; a thread keeps the UI (and clock) responsive.
        return await asyncio.to_thread(get_system_info)

    def show(self, data: SystemInfo) -> None:
        self._row("cpu", "CPU", data.cpu_percent)
        self._row("memory", "RAM", data.memory_percent, _gb(data.memory_used, data.memory_total))
        self._row("disk", "Disk", data.disk_percent, _gb(data.disk_used, data.disk_total))

    def show_error(self, error: Exception) -> None:
        self.query_one("#cpu", Static).update("[$error]⚠ Couldn't load system info[/]")
        self.query_one("#memory", Static).update("")
        self.query_one("#disk", Static).update("")

    def _row(self, widget_id: str, label: str, percent: float, detail: str = "") -> None:
        filled = round(percent / 100 * BAR_WIDTH)
        bar = f"[{_color(percent)}]{'█' * filled}[/][dim]{'░' * (BAR_WIDTH - filled)}[/]"
        text = f"[b]{label:<4}[/] {bar} {percent:>3.0f}%"
        if detail:
            text += f"  [dim]{detail}[/]"
        self.query_one(f"#{widget_id}", Static).update(text)


def _color(percent: float) -> str:
    if percent >= 90:
        return "$error"
    if percent >= 70:
        return "$warning"
    return "$success"


def _gb(used: int, total: int) -> str:
    return f"{used / GB:.1f}/{total / GB:.0f}G"
