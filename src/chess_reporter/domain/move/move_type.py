"""
Chess domain: Move type module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class MoveType(StrEnum):
    """
    Move Type

    Values:
        PLAYED (str): Played move
        MAINLINE (str): Mainline move
        VARIATION (str): Variation move

    """

    PLAYED = "played"
    MAINLINE = "mainline"
    VARIATION = "variation"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)


PRIORITIES: Final[MappingProxyType[MoveType, int]] = MappingProxyType(
    {
        MoveType.PLAYED: 1,
        MoveType.MAINLINE: 2,
        MoveType.VARIATION: 3,
    }
)
