"""
Engine instance: Build engine move sequence module
"""

from __future__ import annotations

from chess import Board, Move


def build_engine_move_sequence(fen: str, moves: list[Move]) -> list[str]:
    """
    Build engine move sequence from the given FEN and list of moves.

    Args:
        fen (str): FEN string representing the chess position
        moves (list[Move]): List of Move objects representing the engine's principal variation

    Returns:
        list[str]: List of UCI strings representing the engine's move sequence.
    """
    current_board: Board = Board(fen)
    engine_move_sequence: list[str] = []

    for move in moves:
        if move not in current_board.legal_moves:
            break

        engine_move_sequence.append(move.uci())
        current_board.push(move)

    return engine_move_sequence
