"""
Chess domain: Get position outcome from board module
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from chess import Board, Outcome, Termination

from chess_reporter.domain.game import GameOutcome, GameResult, GameTermination

RESULT_MAPPING: Final[MappingProxyType[bool | None, GameResult]] = MappingProxyType(
    {
        None: GameResult.DRAW,
        True: GameResult.WHITE_WON,
        False: GameResult.BLACK_WON,
    }
)
TERMINATION_MAPPING: Final[MappingProxyType[Termination, GameTermination]] = MappingProxyType(
    {
        Termination.CHECKMATE: GameTermination.CHECKMATE,
        Termination.STALEMATE: GameTermination.STALEMATE,
        Termination.INSUFFICIENT_MATERIAL: GameTermination.INSUFFICIENT_MATERIAL,
        Termination.SEVENTYFIVE_MOVES: GameTermination.SEVENTYFIVE_MOVES,
        Termination.FIVEFOLD_REPETITION: GameTermination.FIVEFOLD_REPETITION,
        Termination.FIFTY_MOVES: GameTermination.FIFTY_MOVES_RULE,
        Termination.THREEFOLD_REPETITION: GameTermination.THREEFOLD_REPETITION,
    }
)


def get_position_game_outcome_from_board(board: Board) -> GameOutcome:
    """
    Get the position game outcome from a given chess board position.

    Args:
        board (Board): The chess board position to analyze.

    Returns:
        GameOutcome: An object representing the outcome of the game based on the board position.
    """
    outcome: Outcome | None = board.outcome(claim_draw=False)

    if outcome is None:
        return GameOutcome(
            game_result=GameResult.ONGOING,
            game_termination=GameTermination.ONGOING,
        )

    board_termination: Termination = outcome.termination
    board_winner: bool | None = outcome.winner
    game_result: GameResult | None = RESULT_MAPPING.get(board_winner)

    if game_result is None:
        raise ValueError(f"Unsupported winner value from python-chess outcome: {board_winner}")

    game_termination: GameTermination | None = TERMINATION_MAPPING.get(board_termination)

    if game_termination is None:
        raise ValueError(f"Unsupported termination from python-chess outcome: {board_termination}")

    position_outcome: GameOutcome = GameOutcome(
        game_result=game_result,
        game_termination=game_termination,
    )

    return position_outcome
