"""
Chess domain: Game result module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class GameResult(StrEnum):
    """
    Game Result

    Values:
        ONGOING (str): Game is still ongoing
        DRAW (str): Game ended in a draw
        WHITE_WON (str): White won the game
        BLACK_WON (str): Black won the game
    """

    ONGOING = "ongoing"
    DRAW = "draw"
    WHITE_WON = "white_won"
    BLACK_WON = "black_won"

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
    def symbol(self) -> str:
        """
        Symbol
        """

        return SYMBOLS.get(self, "🕳️")

    @property
    def is_finished(self) -> bool:
        """
        Is finished
        """
        return self is not GameResult.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Has winner
        """
        return self in (GameResult.WHITE_WON, GameResult.BLACK_WON)

    @property
    def is_draw(self) -> bool:
        """
        Is draw
        """
        return self is GameResult.DRAW


PRIORITIES: Final[MappingProxyType[GameResult, int]] = MappingProxyType(
    {
        GameResult.ONGOING: 1,
        GameResult.DRAW: 2,
        GameResult.WHITE_WON: 3,
        GameResult.BLACK_WON: 4,
    }
)
CHARACTERS: Final[MappingProxyType[GameResult, str]] = MappingProxyType(
    {
        GameResult.ONGOING: "*",
        GameResult.DRAW: "1/2-1/2",
        GameResult.WHITE_WON: "1-0",
        GameResult.BLACK_WON: "0-1",
    }
)
SYMBOLS: Final[MappingProxyType[GameResult, str]] = MappingProxyType(
    {
        GameResult.ONGOING: "🔄",
        GameResult.DRAW: "🤝",
        GameResult.WHITE_WON: "⚪",
        GameResult.BLACK_WON: "⚫",
    }
)
