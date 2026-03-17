"""
Chess domain: Chess engine instance setup
"""

from __future__ import annotations

from functools import cached_property

from chess import Board
from pydantic import BaseModel, ConfigDict, Field

from chess_reporter.domain.game import GameOutcome
from chess_reporter.domain.position import PositionContext


class EngineContext(BaseModel):
    """
    Engine Context
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    position_context: PositionContext = Field(
        description="The position context for which the chess engine instance will be created",
    )
    analysis_run: int = Field(
        description="Analysis run number",
        ge=1,
    )

    @cached_property
    def board(self) -> Board:
        """
        Board instance representing the chess position
        """
        return self.position_context.board.copy(stack=False)

    @cached_property
    def game_outcome(self) -> GameOutcome:
        """
        Game outcome of the position
        """
        return self.position_context.game_outcome
