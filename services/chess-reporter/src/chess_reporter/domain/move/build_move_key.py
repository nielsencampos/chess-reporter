"""
Chess domain: Build move key module
"""

from __future__ import annotations

from chess import Board, Move

from .move_key import MoveKey


def build_move_key(board: Board, move: Move) -> MoveKey:
    """
    Build a MoveKey from a given chess board position and move.

    Args:
        board (Board): The chess board position to analyze.
        move (Move): The chess move to analyze.

    Returns:
        MoveKey: An object representing the key of the move based on the board position.
    """
    return MoveKey(
        fen=board.fen(),
        uci=move.uci(),
    )
