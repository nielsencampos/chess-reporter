"""
Chess domain: Get position legal moves from board module
"""

from __future__ import annotations

from chess import Board

from chess_reporter.domain.move import MoveContext

from .position_legal_moves import PositionLegalMoves


def get_position_legal_moves_from_board(board: Board) -> PositionLegalMoves:
    """
    Get the legal moves of a chess position from a given chess board.

    Args:
        board (Board): The chess board position to analyze.

    Returns:
        PositionLegalMoves: An object containing the legal moves of the position.
    """
    return PositionLegalMoves(
        [
            MoveContext(
                board_before=board.copy(stack=False),
                move=move,
            )
            for move in board.legal_moves
        ]
    )
