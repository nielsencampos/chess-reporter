"""
Chess domain: Game phase module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class GamePhase(StrEnum):
    """
    Game Phase

    Values:
        OPENING (str): Opening
        MIDDLEGAME (str): Middlegame
        ENDGAME (str): Endgame
    """

    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

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


PRIORITIES: Final[MappingProxyType[GamePhase, int]] = MappingProxyType(
    {
        GamePhase.OPENING: 1,
        GamePhase.MIDDLEGAME: 2,
        GamePhase.ENDGAME: 3,
    }
)
CHARACTERS: Final[MappingProxyType[GamePhase, str]] = MappingProxyType(
    {
        GamePhase.OPENING: ">>",
        GamePhase.MIDDLEGAME: "><",
        GamePhase.ENDGAME: "<<",
    }
)
SYMBOLS: Final[MappingProxyType[GamePhase, str]] = MappingProxyType(
    {
        GamePhase.OPENING: "⏩",
        GamePhase.MIDDLEGAME: "⚔️",
        GamePhase.ENDGAME: "🏁",
    }
)
