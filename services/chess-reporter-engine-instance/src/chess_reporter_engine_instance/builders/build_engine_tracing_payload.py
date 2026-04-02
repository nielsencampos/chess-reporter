"""
Engine instance: Build engine tracing payload module
"""

from __future__ import annotations

from chess import Move
from chess_reporter_schemas.engine import EngineTracingPayload

from .build_engine_move_sequence import build_engine_move_sequence


def build_engine_tracing_payload(
    fen: str,
    currmovenumber: int | None,
    currmove: Move | None,
    currline: dict[int, list[Move]] | None,
) -> EngineTracingPayload:
    """
    Build engine tracing payload containing the current move number, current move,
    and current line moves.

    Args:
        fen (str): FEN string representing the chess position before the tracing information.
        currmovenumber (int | None):
            Current move number reported by the engine during the search, if available.
        currmove (Move | None):
            Current move/UCI reported by the engine during the search, if available.
        currline (dict[int, list[Move]] | None):
            Current line reported by the engine during the search, if available.
            It's a dictionary where the key is the move number and
            the value is a list of moves in UCI format, if available.

    Returns:
        EngineTracingPayload:
            An instance of EngineTracingPayload containing the tracing information.
    """
    current_move_number: int | None = currmovenumber
    current_move: str = currmove.uci() if currmove is not None else ""
    current_line_moves: dict[int, list[str]] | None = None

    if currline is not None:
        current_line_moves = {
            move_number: build_engine_move_sequence(fen, moves)
            for move_number, moves in currline.items()
        }

    return EngineTracingPayload(
        current_move_number=current_move_number,
        current_move=current_move,
        current_line_moves=current_line_moves,
    )
