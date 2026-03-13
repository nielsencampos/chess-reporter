"""
Chess domain: Result type
"""

from __future__ import annotations

from enum import StrEnum


class ResultType(StrEnum):
    """
    Enumeration for the result of the game for a chess position.

    Values:
        ONGOING (str): Indicating that there is no winner or draw yet
        WHITE_WON (str): Represents white player has won the game
        BLACK_WON (str): Represents black player has won the game
        DRAW (str): Indicating that game ended in a draw

    Properties:
        is_finished (bool): Indicating if the game finished
        has_winner (bool): Indicating if the game has a winner
        is_draw (bool): Indicating if the game ended in a draw
    """

    ONGOING = "ongoing"
    WHITE_WON = "white_won"
    BLACK_WON = "black_won"
    DRAW = "draw"

    @property
    def is_finished(self) -> bool:
        """
        Indicating if the game finished
        """
        return self is not ResultType.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Indicating if the game has a winner
        """
        return self in {ResultType.WHITE_WON, ResultType.BLACK_WON}

    @property
    def is_draw(self) -> bool:
        """
        Indicating if the game ended in a draw
        """
        return self is ResultType.DRAW
