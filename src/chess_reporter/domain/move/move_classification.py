"""
Chess domain: Move classification module
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class MoveClassification(StrEnum):
    """
    Move Classification

    Values:
        BOOK (str): A move that is part of the opening book.
        BOOK_TRANSPOSED (str): A move that transposes to a opening book,
            but in a different order.
        BLUNDER (str): A move that significantly loses in evaluation.
        MISS (str): A move that misses the best evaluation possible.
        MISTAKE (str): A move that worsens the evaluation but not as severely as a blunder.
        INACCURACY (str): A move that slightly worsens the evaluation.
        FORCED (str): A move that is the only reasonable option in the position.
        GOOD (str): A move that loses slightly in evaluation, but is still reasonable.
        EXCELLENT (str): A move that is the best move in the position.
        GREAT (str): The only move that maintains the evaluation.
        BRILLIANT (str): The only move that maintains the evaluation losing material.
    """

    BOOK = "book"
    BOOK_TRANSPOSED = "book transposed"
    BLUNDER = "blunder"
    MISS = "miss"
    MISTAKE = "mistake"
    INACCURACY = "inaccuracy"
    FORCED = "forced"
    GOOD = "good"
    EXCELLENT = "excellent"
    GREAT = "great"
    BRILLIANT = "brilliant"

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


PRIORITIES: Final[MappingProxyType[MoveClassification, int]] = MappingProxyType(
    {
        MoveClassification.BOOK: 1,
        MoveClassification.BOOK_TRANSPOSED: 2,
        MoveClassification.BLUNDER: 3,
        MoveClassification.MISS: 4,
        MoveClassification.MISTAKE: 5,
        MoveClassification.INACCURACY: 6,
        MoveClassification.FORCED: 7,
        MoveClassification.GOOD: 8,
        MoveClassification.EXCELLENT: 9,
        MoveClassification.GREAT: 10,
        MoveClassification.BRILLIANT: 11,
    }
)

CHARACTERS: Final[MappingProxyType[MoveClassification, str]] = MappingProxyType(
    {
        MoveClassification.BOOK: "B",
        MoveClassification.BOOK_TRANSPOSED: "~B",
        MoveClassification.BLUNDER: "??",
        MoveClassification.MISS: "X",
        MoveClassification.MISTAKE: "?",
        MoveClassification.INACCURACY: "?!",
        MoveClassification.FORCED: "*",
        MoveClassification.GOOD: "V",
        MoveClassification.EXCELLENT: "VV",
        MoveClassification.GREAT: "!",
        MoveClassification.BRILLIANT: "!!",
    }
)

SYMBOLS: Final[MappingProxyType[MoveClassification, str]] = MappingProxyType(
    {
        MoveClassification.BOOK: "📖",
        MoveClassification.BOOK_TRANSPOSED: "📑",
        MoveClassification.BLUNDER: "🚨",
        MoveClassification.MISS: "⛔",
        MoveClassification.MISTAKE: "⚠️",
        MoveClassification.INACCURACY: "⚡",
        MoveClassification.FORCED: "🧷",
        MoveClassification.GOOD: "🟢",
        MoveClassification.EXCELLENT: "✅",
        MoveClassification.GREAT: "🔷",
        MoveClassification.BRILLIANT: "💎",
    }
)
