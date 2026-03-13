"""
Chess domain: Turn type
"""

from __future__ import annotations

from enum import StrEnum


class TurnType(StrEnum):
    """
    Enumeration for the turn to move in the chess position, which can be either 'white' or 'black'.

    Values:
        WHITE (str): White to move
        BLACK (str): Black to move

    Properties:
        opposite: The opposite turn to move
        label: Human-readable label for the turn
    """

    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> TurnType:
        """
        The opposite turn to move
        """
        if self == TurnType.WHITE:
            return TurnType.BLACK
        else:
            return TurnType.WHITE

    @property
    def label(self) -> str:
        """
        Human-readable label for the turn
        """
        if self == TurnType.WHITE:
            return "White to move"
        else:
            return "Black to move"
