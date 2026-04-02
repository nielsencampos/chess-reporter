"""
Schemas: API health status type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class APIHealthStatusType(StrEnum):
    """
    API Health Status Type

    Values:
        OK: API is healthy and functioning properly
        WARNING: API is experiencing issues but still operational
        ERROR: API is unhealthy and not functioning properly
    """

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)

    @property
    def description(self) -> str:
        """
        Description
        """
        return DESCRIPTIONS.get(self, "Unknown status type")


PRIORITIES: Final[MappingProxyType[APIHealthStatusType, int]] = MappingProxyType(
    {
        APIHealthStatusType.OK: 1,
        APIHealthStatusType.WARNING: 2,
        APIHealthStatusType.ERROR: 3,
    }
)
DESCRIPTIONS: Final[MappingProxyType[APIHealthStatusType, str]] = MappingProxyType(
    {
        APIHealthStatusType.OK: "API is healthy and functioning properly",
        APIHealthStatusType.WARNING: "API is experiencing issues but still operational",
        APIHealthStatusType.ERROR: "API is unhealthy and not functioning properly",
    }
)
