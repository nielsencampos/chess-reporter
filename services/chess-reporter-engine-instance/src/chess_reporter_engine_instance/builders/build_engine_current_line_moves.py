"""
Engine instance: Build engine current line moves module
"""

from __future__ import annotations

from chess import Move

from .build_engine_move_sequence import build_engine_move_sequence


def build_engine_current_line_moves(
    fen: str,
    current_line: dict[int, list[Move]],
) -> list[tuple[int, list[str]]]:
    """
    Build engine current line moves from the given FEN and current line dictionary.

    Args:
        fen: FEN string representing the chess position
        current_line:
            Dictionary mapping move index to list of Move objects representing
            the engine's current line

    Returns:
        List of tuples containing move index and list of UCI strings representing
        the engine's current line moves.
    """

    return [
        (index, build_engine_move_sequence(fen, moves)) for index, moves in current_line.items()
    ]
