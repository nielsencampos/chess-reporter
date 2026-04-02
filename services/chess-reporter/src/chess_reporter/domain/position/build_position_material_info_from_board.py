"""
Chess domain: Build position material info from board module
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from chess import (
    BISHOP,
    BLACK,
    KNIGHT,
    PAWN,
    QUEEN,
    ROOK,
    WHITE,
    Board,
    PieceType,
)

from .position_material_info import PositionMaterialInfo

PIECE_VALUES: Final[MappingProxyType[PieceType, int]] = MappingProxyType(
    {
        PAWN: 100,
        KNIGHT: 300,
        BISHOP: 300,
        ROOK: 500,
        QUEEN: 900,
    }
)


def build_position_material_info_from_board(board: Board) -> PositionMaterialInfo:
    """
    Build the material information of a chess position from a given chess board.

    Args:
        board (Board): The chess board position to analyze.

    Returns:
        PositionMaterialInfo: An object containing the material information of the position,
            including total material and piece counts for both sides.
    """
    white_material: int = 0
    white_piece_count: int = 1  # Kings are always counted, but not valued
    black_material: int = 0
    black_piece_count: int = 1  # Kings are always counted, but not valued

    for piece_type, value in PIECE_VALUES.items():
        white_pieces = len(board.pieces(piece_type, WHITE))
        black_pieces = len(board.pieces(piece_type, BLACK))
        white_material += white_pieces * value
        black_material += black_pieces * value
        white_piece_count += white_pieces
        black_piece_count += black_pieces

    return PositionMaterialInfo(
        white_material=white_material,
        white_piece_count=white_piece_count,
        black_material=black_material,
        black_piece_count=black_piece_count,
    )
