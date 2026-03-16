"""
Chess domain: Build engine current line moves module
"""

from __future__ import annotations

from chess import Board, Move

from chess_reporter.domain.move import MoveContext

from .build_move_sequence import build_move_sequence


def build_engine_current_line_moves(
    board: Board,
    current_line: dict[int, list[Move]],
) -> list[tuple[int, list[MoveContext]]]:
    """
    Build engine current line moves as a list of tuples containing analysis indices
    and their corresponding move-context sequences.

    Args:
        board (Board): Board position before the current line moves.
        current_line (dict[int, list[Move]]): Mapping of analysis indices to their
            current line move sequences.

    Returns:
        list[tuple[int, list[MoveContext]]]: List of tuples containing each analysis
            index and its corresponding move contexts.
    """
    return [(index, build_move_sequence(board, moves)) for index, moves in current_line.items()]
