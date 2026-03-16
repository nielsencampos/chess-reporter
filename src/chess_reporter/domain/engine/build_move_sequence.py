"""
Chess domain: Build move sequence helper module
"""

from __future__ import annotations

from chess import Board, Move

from chess_reporter.domain.move import MoveContext


def build_move_sequence(board: Board, moves: list[Move]) -> list[MoveContext]:
    """
    Build a sequence of MoveContext objects from a list of moves on a given board.

    Iterates through the moves in order, creating a MoveContext for each legal move
    and advancing the board. Stops at the first illegal move.

    Args:
        board (Board): Board position to start from (not mutated — a copy is used internally).
        moves (list[Move]): Ordered list of moves to walk.

    Returns:
        list[MoveContext]: MoveContext objects for each legal move played in sequence.
    """
    current_board: Board = board.copy(stack=False)
    result: list[MoveContext] = []

    for move in moves:
        if move not in current_board.legal_moves:
            break

        result.append(MoveContext(board_before=current_board.copy(stack=False), move=move))
        current_board.push(move)

    return result
