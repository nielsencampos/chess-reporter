"""
Schemas: API response status type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class APIResponseStatusType(StrEnum):
    """
    API Response Status Type

    Values:
        QUEUED: The request has been received and is waiting to be processed
        REJECTED: The request has been rejected
        IN_PROGRESS: The request is currently being processed
        COMPLETED: The request has been successfully processed
        FAILED: The request has failed to be processed
    """

    QUEUED = "queued"
    REJECTED = "rejected"
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
    def description(self) -> str:
        """
        Description
        """
        return DESCRIPTIONS.get(self, "Unknown status type")


PRIORITIES: Final[MappingProxyType[APIResponseStatusType, int]] = MappingProxyType(
    {
        APIResponseStatusType.QUEUED: 1,
        APIResponseStatusType.REJECTED: 2,
        APIResponseStatusType.IN_PROGRESS: 3,
        APIResponseStatusType.COMPLETED: 4,
        APIResponseStatusType.FAILED: 5,
    }
)
DESCRIPTIONS: Final[MappingProxyType[APIResponseStatusType, str]] = MappingProxyType(
    {
        APIResponseStatusType.QUEUED: (
            "The request has been received and is waiting to be processed"
        ),
        APIResponseStatusType.REJECTED: "The request has been rejected",
        APIResponseStatusType.IN_PROGRESS: "The request is currently being processed",
        APIResponseStatusType.COMPLETED: "The request has been successfully processed",
        APIResponseStatusType.FAILED: "The request has failed to be processed",
    }
)
