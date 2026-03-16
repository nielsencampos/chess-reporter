"""
Chess domain: Position turn module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class PositionTurn(StrEnum):
    """
    Position Turn

    Values:
        WHITE (str): White to move
        BLACK (str): Black to move
    """

    WHITE = "white"
    BLACK = "black"

    @property
    def priority(self) -> int:
        """
        Priority
        """
        return PRIORITIES.get(self, 0)

    @property
    def character(self) -> str:
        """
        Character
        """

        return CHARACTERS.get(self, "∅")

    @property
    def opposite(self) -> PositionTurn:
        """
        The opposite turn to move
        """
        if self is PositionTurn.WHITE:
            return PositionTurn.BLACK

        return PositionTurn.WHITE

    @property
    def label(self) -> str:
        """
        Human-readable label for the turn
        """
        if self is PositionTurn.WHITE:
            return "White to move"

        return "Black to move"


PRIORITIES: Final[MappingProxyType[PositionTurn, int]] = MappingProxyType(
    {
        PositionTurn.WHITE: 1,
        PositionTurn.BLACK: 2,
    }
)
CHARACTERS: Final[MappingProxyType[PositionTurn, str]] = MappingProxyType(
    {
        PositionTurn.WHITE: "W",
        PositionTurn.BLACK: "B",
    }
)
