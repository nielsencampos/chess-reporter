"""
Chess domain: Move key module
"""

from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field

from chess_reporter.utils.safe_string import safe_string


class MoveKey(BaseModel):
    """
    Move Key
    """

    model_config = ConfigDict(frozen=True)

    fen: str = Field(
        description="FEN string representing the chess position from where the move is being made",
        min_length=20,
        max_length=100,
    )
    uci: str = Field(
        description="UCI string representing the chess move",
        min_length=4,
        max_length=10,
    )

    @cached_property
    def trace(self) -> dict[str, str]:
        """
        Trace representation of the move key
        """
        return {
            "fen": self.fen,
            "uci": self.uci,
        }

    @cached_property
    def safe_string(self) -> str:
        """
        Safe string representation of the move key
        """
        return safe_string(self.trace)
