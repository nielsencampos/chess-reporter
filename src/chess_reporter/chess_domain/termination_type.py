"""
Chess domain: Termination type
"""

from __future__ import annotations

from enum import StrEnum


class TerminationType(StrEnum):
    """
    Enumeration for the termination condition of the game for a chess position.

    Values:
        ONGOING (str): Game is ongoing
        ABANDONMENT (str): Game was abandoned
        CHECKMATE (str): Game finished by checkmate
        RESIGNATION (str): Game finished by resignation
        TIMEOUT (str): Game finished by timeout (win)
        VARIANT (str): Game finished by variant rules
        DRAW_BY_AGREEMENT (str): Game ended in a draw by agreement
        TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL (str): Game ended in a draw due to timeout
            and insufficient material
        STALEMATE (str): Game ended in a stalemate
        INSUFFICIENT_MATERIAL (str): Game ended in a draw due to insufficient material
        THREEFOLD_REPETITION (str): Game ended in a draw due to threefold repetition
        FIFTY_MOVES_RULE (str): Game ended in a draw due to the fifty-move rule
        FIVEFOLD_REPETITION (str): Game ended in a draw due to fivefold repetition
        SEVENTYFIVE_MOVES (str): Game ended in a draw due to seventy-five moves rule
        VARIANT_DRAW (str): Game ended in a draw due to variant rules

    Properties:
        is_finished (bool): Indicating if the game finished
        has_winner (bool): Indicating if the game has a winner
        is_draw (bool): Indicating if the game ended in a draw
    """

    ONGOING = "ongoing"
    ABANDONMENT = "abandonment"
    CHECKMATE = "checkmate"
    RESIGNATION = "resignation"
    TIMEOUT = "timeout"
    VARIANT = "variant"
    DRAW_BY_AGREEMENT = "draw_by_agreement"
    TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL = "timeout_draw_by_insufficient_material"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    THREEFOLD_REPETITION = "threefold_repetition"
    FIFTY_MOVES_RULE = "fifty_moves_rule"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    VARIANT_DRAW = "variant_draw"

    @property
    def is_finished(self) -> bool:
        """
        Indicating if the game finished
        """
        return self is not TerminationType.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Indicating if the game has a winner
        """
        return self in {
            TerminationType.ABANDONMENT,
            TerminationType.CHECKMATE,
            TerminationType.RESIGNATION,
            TerminationType.TIMEOUT,
            TerminationType.VARIANT,
        }

    @property
    def is_draw(self) -> bool:
        """
        Indicating if the game ended in a draw
        """
        return self in {
            TerminationType.DRAW_BY_AGREEMENT,
            TerminationType.TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL,
            TerminationType.STALEMATE,
            TerminationType.INSUFFICIENT_MATERIAL,
            TerminationType.THREEFOLD_REPETITION,
            TerminationType.FIFTY_MOVES_RULE,
            TerminationType.FIVEFOLD_REPETITION,
            TerminationType.SEVENTYFIVE_MOVES,
            TerminationType.VARIANT_DRAW,
        }
