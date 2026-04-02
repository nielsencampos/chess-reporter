"""
Engine instance: Build engine variation payload module
"""

from __future__ import annotations

from chess import Move
from chess_reporter_schemas.engine import EngineVariationPayload

from .build_engine_move_sequence import build_engine_move_sequence
from .build_engine_refutation_moves import build_engine_refutation_moves


def build_engine_variation_payload(
    fen: str,
    pv: list[Move] | None,
    refutation: dict[Move, list[Move]] | None,
) -> EngineVariationPayload:
    """
    Build engine variation payload containing the variation moves and refutation moves.

    Args:
        fen (str): FEN string representing the chess position before the variation.
        pv (list[Move] | None): List of moves in the principal variation.
        refutation (dict[Move, list[Move]] | None):
            Mapping of candidate moves to their refutation move sequences.

    Returns:
        EngineVariationPayload:
            An instance of EngineVariationPayload containing the variation moves
            and refutation moves.
    """
    variation_moves: list[str] | None = (
        build_engine_move_sequence(fen, pv) if pv is not None else None
    )
    refutation_moves: list[tuple[str, list[str]]] | None = (
        build_engine_refutation_moves(fen, refutation) if refutation is not None else None
    )

    return EngineVariationPayload(
        variation_moves=variation_moves,
        refutation_moves=refutation_moves,
    )
