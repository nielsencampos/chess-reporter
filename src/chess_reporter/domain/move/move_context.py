"""
Chess domain: Move context module
"""

from __future__ import annotations

from functools import cached_property

from chess import Board, Move
from pydantic import BaseModel, ConfigDict, Field


class MoveContext(BaseModel):
    """
    Move Context
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    board_before: Board = Field(
        description="Board instance representing the chess position before the move is played",
        default_factory=Board,
    )
    move: Move = Field(description="Move instance representing the chess move")

    @property
    def move_uci(self) -> str:
        """
        UCI string representing the chess move
        """
        return self.move.uci()

    @cached_property
    def move_san(self) -> str:
        """
        SAN string representing the chess move
        """
        return self.board_before.san(self.move)

    @cached_property
    def move_is_capture(self) -> bool:
        """
        Flag indicating if the move is a capture
        """
        return self.board_before.is_capture(self.move)

    @cached_property
    def move_is_castling(self) -> bool:
        """
        Flag indicating if the move is a castling move
        """
        return self.board_before.is_castling(self.move)

    @cached_property
    def move_is_en_passant(self) -> bool:
        """
        Flag indicating if the move is an en passant capture
        """
        return self.board_before.is_en_passant(self.move)

    @cached_property
    def move_is_promotion(self) -> bool:
        """
        Flag indicating if the move is a promotion
        """
        return self.move.promotion is not None

    @cached_property
    def board_after(self) -> Board:
        """
        Board instance representing the chess position after the move is played
        """
        board_after: Board = self.board_before.copy(stack=False)
        board_after.push(self.move)

        return board_after

    @property
    def move_is_check(self) -> bool:
        """
        Flag indicating if the move gives check
        """
        return self.board_after.is_check()

    @property
    def move_is_checkmate(self) -> bool:
        """
        Flag indicating if the move gives checkmate
        """
        return self.board_after.is_checkmate()

    @property
    def move_is_stalemate(self) -> bool:
        """
        Flag indicating if the move results in stalemate
        """
        return self.board_after.is_stalemate()
