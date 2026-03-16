"""
Utils package: get logic CPU available module
"""

from __future__ import annotations

from psutil import cpu_count, cpu_percent


def get_logic_cpu_available() -> int:
    """
    Get the number of logical CPUs available for use, considering current CPU usage.

    Returns:
        int: The number of logical CPUs available for use, ensuring at least one CPU is always
            available.
    """
    max_cpus: int = max(1, (cpu_count(logical=True) or 1) - 1)
    current_usage: list[float] = cpu_percent(interval=1, percpu=True)
    current_available: int = sum(1 for cpu in current_usage if cpu < 50.0)

    return max(1, min(max_cpus, current_available))
