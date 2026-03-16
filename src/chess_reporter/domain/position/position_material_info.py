"""
Chess domain: Position material info module
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from chess_reporter.domain.game import GamePhase


class PositionMaterialInfo(BaseModel):
    """
    Position Material Info
    """

    model_config = ConfigDict(frozen=True)

    white_material: int = Field(
        description="Total material for White",
        ge=0,
    )
    white_piece_count: int = Field(
        description="Total number of pieces for White",
        ge=0,
    )
    black_material: int = Field(
        description="Total material for Black",
        ge=0,
    )
    black_piece_count: int = Field(
        description="Total number of pieces for Black",
        ge=0,
    )

    @property
    def overall_material(self) -> int:
        """
        Total material remaining on the board
        """
        return self.white_material + self.black_material

    @property
    def overall_piece_count(self) -> int:
        """
        Total number of pieces remaining on the board
        """
        return self.white_piece_count + self.black_piece_count

    @property
    def material_balance(self) -> int:
        """
        Material balance indicating which side has more material
        """
        return self.white_material - self.black_material

    @property
    def piece_count_balance(self) -> int:
        """
        Piece count balance indicating which side has more pieces
        """
        return self.white_piece_count - self.black_piece_count

    @property
    def material_game_phase(self) -> GamePhase:
        """
        Determine the game phase based on remaining piece count
        """
        if self.overall_piece_count >= 26:
            return GamePhase.OPENING

        if self.overall_piece_count >= 12:
            return GamePhase.MIDDLEGAME

        return GamePhase.ENDGAME
