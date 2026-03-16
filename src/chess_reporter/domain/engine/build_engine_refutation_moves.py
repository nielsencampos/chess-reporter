"""
Chess domain: Build engine refutation moves module
"""

from __future__ import annotations

from chess import Board, Move

from chess_reporter.domain.move import MoveContext

from .build_move_sequence import build_move_sequence


def build_engine_refutation_moves(
    board: Board,
    refutation: dict[Move, list[Move]],
) -> list[tuple[MoveContext, list[MoveContext]]]:
    """
    Build engine refutation moves as a list of tuples containing move contexts
    and their corresponding refutation move-context sequences.

    Args:
        board (Board): Board position before the refutation.
        refutation (dict[Move, list[Move]]): Mapping of candidate moves to their
            refutation move sequences.

    Returns:
        list[tuple[MoveContext, list[MoveContext]]]: List of tuples containing each
            candidate move context and its corresponding refutation move contexts.
    """
    engine_refutation_moves: list[tuple[MoveContext, list[MoveContext]]] = []

    for move, refutation_moves in refutation.items():
        current_board: Board = board.copy(stack=False)

        if move not in current_board.legal_moves:
            continue

        move_context: MoveContext = MoveContext(
            board_before=current_board.copy(stack=False),
            move=move,
        )

        current_board.push(move)
        refutation_contexts: list[MoveContext] = build_move_sequence(
            current_board, refutation_moves
        )

        engine_refutation_moves.append((move_context, refutation_contexts))

    return engine_refutation_moves
