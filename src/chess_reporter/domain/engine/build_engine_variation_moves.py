"""
Chess domain: Build engine variation moves module
"""

from __future__ import annotations

from chess import Board, Move

from chess_reporter.domain.move import MoveContext

from .build_move_sequence import build_move_sequence


def build_engine_variation_moves(board: Board, moves: list[Move]) -> list[MoveContext]:
    """
    Build the engine variation as a list of MoveContext objects representing the moves in the
    principal variation along with their corresponding board positions.

    Args:
        board (Board): Board position before the variation
        moves (list[Move]): List of moves in the variation

    Returns:
        list[MoveContext]: List of MoveContext objects representing the engine variation.
    """
    return build_move_sequence(board, moves)
