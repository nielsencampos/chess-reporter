"""
Chess domain: Game termination module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class GameTermination(StrEnum):
    """
    Game Termination

    Values:
        ONGOING (str): Game is ongoing
        AGREEMENT (str): Game ended in a draw by agreement
        FIFTY_MOVES_RULE (str): Game ended in a draw due to the fifty-move rule
        FIVEFOLD_REPETITION (str): Game ended in a draw due to fivefold repetition
        INSUFFICIENT_MATERIAL (str): Game ended in a draw due to insufficient material
        SEVENTYFIVE_MOVES (str): Game ended in a draw due to seventy-five moves rule
        STALEMATE (str): Game ended in a stalemate
        THREEFOLD_REPETITION (str): Game ended in a draw due to threefold repetition
        TIMEOUT_DRAW (str): Game finished by timeout with a draw due to insufficient material
        ABANDONMENT (str): Game was abandoned
        CHECKMATE (str): Game finished by checkmate
        FORFEIT (str): Game finished by forfeit (e.g., illegal move)
        RESIGNATION (str): Game finished by resignation
        TIMEOUT_WIN (str): Game finished by timeout (win)
    """

    ONGOING = "ongoing"
    AGREEMENT = "agreement"
    FIFTY_MOVES_RULE = "fifty_moves_rule"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    STALEMATE = "stalemate"
    THREEFOLD_REPETITION = "threefold_repetition"
    TIMEOUT_DRAW = "timeout_draw"
    ABANDONMENT = "abandonment"
    CHECKMATE = "checkmate"
    FORFEIT = "forfeit"
    RESIGNATION = "resignation"
    TIMEOUT_WIN = "timeout_win"

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
    def is_finished(self) -> bool:
        """
        Is finished
        """
        return self is not GameTermination.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Has winner
        """
        return self in {
            GameTermination.ABANDONMENT,
            GameTermination.CHECKMATE,
            GameTermination.FORFEIT,
            GameTermination.RESIGNATION,
            GameTermination.TIMEOUT_WIN,
        }

    @property
    def is_draw(self) -> bool:
        """
        Is draw
        """
        return self in {
            GameTermination.AGREEMENT,
            GameTermination.FIFTY_MOVES_RULE,
            GameTermination.FIVEFOLD_REPETITION,
            GameTermination.INSUFFICIENT_MATERIAL,
            GameTermination.SEVENTYFIVE_MOVES,
            GameTermination.STALEMATE,
            GameTermination.THREEFOLD_REPETITION,
            GameTermination.TIMEOUT_DRAW,
        }


PRIORITIES: Final[MappingProxyType[GameTermination, int]] = MappingProxyType(
    {
        GameTermination.ONGOING: 1,
        GameTermination.AGREEMENT: 2,
        GameTermination.FIFTY_MOVES_RULE: 3,
        GameTermination.FIVEFOLD_REPETITION: 4,
        GameTermination.INSUFFICIENT_MATERIAL: 5,
        GameTermination.SEVENTYFIVE_MOVES: 6,
        GameTermination.STALEMATE: 7,
        GameTermination.THREEFOLD_REPETITION: 8,
        GameTermination.TIMEOUT_DRAW: 9,
        GameTermination.ABANDONMENT: 10,
        GameTermination.CHECKMATE: 11,
        GameTermination.FORFEIT: 12,
        GameTermination.RESIGNATION: 13,
        GameTermination.TIMEOUT_WIN: 14,
    }
)
CHARACTERS: Final[MappingProxyType[GameTermination, str]] = MappingProxyType(
    {
        GameTermination.ONGOING: "*",
        GameTermination.AGREEMENT: "=",
        GameTermination.FIFTY_MOVES_RULE: "50",
        GameTermination.FIVEFOLD_REPETITION: "5X",
        GameTermination.INSUFFICIENT_MATERIAL: "IM",
        GameTermination.SEVENTYFIVE_MOVES: "75",
        GameTermination.STALEMATE: "SM",
        GameTermination.THREEFOLD_REPETITION: "3X",
        GameTermination.TIMEOUT_DRAW: "TD",
        GameTermination.ABANDONMENT: "AB",
        GameTermination.CHECKMATE: "#",
        GameTermination.FORFEIT: "FF",
        GameTermination.RESIGNATION: "RG",
        GameTermination.TIMEOUT_WIN: "TW",
    }
)
