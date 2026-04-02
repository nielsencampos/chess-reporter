"""
Engine instance: Build engine refutation moves module
"""

from __future__ import annotations

from chess import Board, Move

from .build_engine_move_sequence import build_engine_move_sequence


def build_engine_refutation_moves(
    fen: str,
    refutation: dict[Move, list[Move]],
) -> list[tuple[str, list[str]]]:
    """
    Build engine refutation moves as a list of tuples containing move contexts
    and their corresponding refutation move-context sequences.

    Args:
        fen (str): FEN string representing the chess position before the refutation.
        refutation (dict[Move, list[Move]]):
            Mapping of candidate moves to their refutation move sequences.

    Returns:
        list[tuple[str, list[str]]]: List of tuples containing each
            candidate move context and its corresponding refutation move contexts.
    """
    engine_refutation_moves: list[tuple[str, list[str]]] = []

    for refutation_move, refutation_moves in refutation.items():
        current_board: Board = Board(fen)

        if refutation_move not in current_board.legal_moves:
            continue

        refutation_move_uci: str = refutation_move.uci()

        current_board.push(refutation_move)
        refutation_moves_uci: list[str] = build_engine_move_sequence(
            current_board.fen(), refutation_moves
        )

        engine_refutation_moves.append((refutation_move_uci, refutation_moves_uci))

    return engine_refutation_moves
