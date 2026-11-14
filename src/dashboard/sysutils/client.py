from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class SystemInfo:
    cpu_percent: float
    memory_used: int
    memory_total: int
    memory_percent: float
    disk_used: int
    disk_total: int
    disk_percent: float


def get_system_info() -> SystemInfo:
    """Sample system usage. Blocks for ~0.5s while measuring CPU, so call it from a thread."""
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return SystemInfo(
        cpu_percent=cpu,
        memory_used=memory.total - memory.available,
        memory_total=memory.total,
        memory_percent=memory.percent,
        disk_used=disk.used,
        disk_total=disk.total,
        disk_percent=disk.percent,
    )
