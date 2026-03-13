"""
Chess domain: Classification type
"""

from __future__ import annotations

from enum import StrEnum


class ClassificationType(StrEnum):
    """
    Enumeration for the classification of a chess move based on its quality.

        Values:
            BLUNDER (str): A move that significantly worsens the position.
            MISTAKE (str): A move that worsens the position but not as severely as a blunder.
            INACCURACY (str): A move that is not the best but does not significantly worsen the
                position.
            GOOD (str): A move that is better than the average move but not the best.
            EXCELLENT (str): A move that is the best move in the position.
            GREAT (str): A move that is exceptionally good and often surprising.
            BRILLIANT (str): A move that is exceptionally good and often surprising.
    """

    BLUNDER = "Blunder"
    MISTAKE = "Mistake"
    INACCURACY = "Inaccuracy"
    GOOD = "Good"
    EXCELLENT = "Excellent"
    GREAT = "Great"
    BRILLIANT = "Brilliant"

    @property
    def symbol(self) -> str:
        """
        Get the symbol associated with the classification type.

        Returns:
            str: The symbol representing the classification type.
        """
        symbols = {
            ClassificationType.BLUNDER: "??",
            ClassificationType.MISTAKE: "?",
            ClassificationType.INACCURACY: "?!",
            ClassificationType.GOOD: "!",
            ClassificationType.EXCELLENT: "!!",
            ClassificationType.GREAT: "!!",
            ClassificationType.BRILLIANT: "!!",
        }
        return symbols[self]
