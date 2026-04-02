"""
Chess domain: Game outcome module
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from chess_reporter.utils.safe_string import safe_string

from .game_result import GameResult
from .game_termination import GameTermination


class GameOutcome(BaseModel):
    """
    Game Outcome
    """

    model_config = ConfigDict(frozen=True)

    game_result: GameResult = Field(
        description="Result condition of the game",
    )
    game_termination: GameTermination = Field(
        description="Termination condition of the game",
    )

    @model_validator(mode="after")
    def validate_game_outcome(self) -> GameOutcome:
        if (
            self.game_result.is_finished != self.game_termination.is_finished
            or self.game_result.has_winner != self.game_termination.has_winner
            or self.game_result.is_draw != self.game_termination.is_draw
        ):
            raise ValueError(
                "Inconsistent game outcome: result and termination must both "
                "indicate the same outcome"
            )

        return self

    @property
    def is_finished(self) -> bool:
        """
        Is finished
        """
        return self.game_result.is_finished

    @property
    def has_winner(self) -> bool:
        """
        Has winner
        """
        return self.game_result.has_winner

    @property
    def is_draw(self) -> bool:
        """
        Is draw
        """
        return self.game_result.is_draw

    @property
    def trace(self) -> dict[str, str]:
        """
        Trace representation of the game outcome
        """
        return {
            "game_result": self.game_result.value,
            "game_termination": self.game_termination.value,
        }

    @property
    def safe_string(self) -> str:
        """
        Safe string representation of the game outcome
        """
        return safe_string(f"{self.game_result.value}_{self.game_termination.value}")
