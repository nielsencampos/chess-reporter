"""
Chess domain: Data status module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class DataStatus(StrEnum):
    """
    Data Status

    Values:
        PENDING: Pending status
        IN_PROGRESS: In progress status
        COMPLETED: Completed status
        FAILED: Failed status
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)

    @property
    def name(self) -> str:
        """
        Name
        """
        return NAMES.get(self, "Unknown")

    @property
    def description(self) -> str:
        """
        Description
        """
        return DESCRIPTIONS.get(self, "No description available")


PRIORITIES: Final[MappingProxyType[DataStatus, int]] = MappingProxyType(
    {
        DataStatus.PENDING: 1,
        DataStatus.IN_PROGRESS: 2,
        DataStatus.COMPLETED: 3,
        DataStatus.FAILED: 4,
    }
)
NAMES: Final[MappingProxyType[DataStatus, str]] = MappingProxyType(
    {
        DataStatus.PENDING: "Pending",
        DataStatus.IN_PROGRESS: "In progress",
        DataStatus.COMPLETED: "Completed",
        DataStatus.FAILED: "Failed",
    }
)
DESCRIPTIONS: Final[MappingProxyType[DataStatus, str]] = MappingProxyType(
    {
        DataStatus.PENDING: "Processing has not started yet (in queue)",
        DataStatus.IN_PROGRESS: "Currently being processed",
        DataStatus.COMPLETED: "Processing finished successfully",
        DataStatus.FAILED: "Processing failed",
    }
)
