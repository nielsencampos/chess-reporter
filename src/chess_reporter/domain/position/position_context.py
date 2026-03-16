"""
Chess domain: Position context module
"""

from __future__ import annotations

from functools import cached_property

from chess import Board
from pydantic import BaseModel, ConfigDict, Field, computed_field

from chess_reporter.domain.game import (
    GameOutcome,
    GamePhase,
    GameResult,
    GameTermination,
)

from .get_position_game_outcome_from_board import get_position_game_outcome_from_board
from .get_position_legal_moves_from_board import get_position_legal_moves_from_board
from .get_position_material_info_from_board import get_position_material_info_from_board
from .position_legal_moves import PositionLegalMoves
from .position_material_info import PositionMaterialInfo
from .position_turn import PositionTurn


class PositionContext(BaseModel):
    """
    Position Context
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    board: Board = Field(
        description="Board instance representing the chess position",
        default_factory=Board,
    )
    game_outcome_input: GameOutcome | None = Field(
        description="Optional informed position outcome status of the position evaluation",
        default=None,
    )

    @computed_field
    @property
    def fen(self) -> str:
        """
        FEN string representing the chess position
        """
        return self.board.fen()

    @computed_field
    @property
    def chess960(self) -> bool:
        """
        Flag indicating the position originates from a Chess960 (Fischer Random) game
        """
        return self.board.chess960

    @computed_field
    @property
    def ascii_board(self) -> str:
        """
        ASCII representation of the chess board
        """
        return str(self.board)

    @computed_field
    @cached_property
    def game_outcome(self) -> GameOutcome:
        """
        Outcome status of the position evaluation
        """
        if self.game_outcome_input is not None:
            return self.game_outcome_input

        return get_position_game_outcome_from_board(self.board)

    @computed_field
    @property
    def game_termination(self) -> GameTermination:
        """
        game_termination status of the position evaluation
        """
        return self.game_outcome.game_termination

    @computed_field
    @property
    def game_result(self) -> GameResult:
        """
        game_result of the position evaluation
        """
        return self.game_outcome.game_result

    @computed_field
    @property
    def turn(self) -> PositionTurn:
        """
        Player to move: white or black.
        """
        return PositionTurn.WHITE if self.board.turn else PositionTurn.BLACK

    @computed_field
    @cached_property
    def material_info(self) -> PositionMaterialInfo:
        """
        Material information of the chess position
        """
        return get_position_material_info_from_board(self.board)

    @computed_field
    @property
    def white_material(self) -> int:
        """
        Total material for White
        """
        return self.material_info.white_material

    @computed_field
    @property
    def white_piece_count(self) -> int:
        """
        Total number of pieces for White
        """
        return self.material_info.white_piece_count

    @computed_field
    @property
    def black_material(self) -> int:
        """
        Total material for Black
        """
        return self.material_info.black_material

    @computed_field
    @property
    def black_piece_count(self) -> int:
        """
        Total number of pieces for Black
        """
        return self.material_info.black_piece_count

    @computed_field
    @property
    def overall_material(self) -> int:
        """
        Total material remaining on the board
        """
        return self.material_info.overall_material

    @computed_field
    @property
    def overall_piece_count(self) -> int:
        """
        Total number of pieces remaining on the board
        """
        return self.material_info.overall_piece_count

    @computed_field
    @property
    def material_balance(self) -> int:
        """
        Material balance indicating which side has more material
        """
        return self.material_info.material_balance

    @computed_field
    @property
    def piece_count_balance(self) -> int:
        """
        Piece count balance indicating which side has more pieces
        """
        return self.material_info.piece_count_balance

    @computed_field
    @property
    def material_game_phase(self) -> GamePhase:
        """
        Determine the game phase based on material balance
        """
        return self.material_info.material_game_phase

    @computed_field
    @cached_property
    def legal_moves(self) -> PositionLegalMoves:
        """
        Legal moves available in the position
        """
        return get_position_legal_moves_from_board(self.board)

    @computed_field
    @property
    def legal_moves_count(self) -> int:
        """
        Count of legal moves available in the position
        """
        return self.legal_moves.count

    @computed_field
    @cached_property
    def captures(self) -> PositionLegalMoves:
        """
        Legal moves in the position that are captures
        """
        return self.legal_moves.captures

    @computed_field
    @property
    def captures_count(self) -> int:
        """
        Count of legal moves in the position that are captures
        """
        return self.legal_moves.captures_count
