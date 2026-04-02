"""
Chess domain: Position key module
"""

from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field

from chess_reporter.utils.safe_string import safe_string


class PositionKey(BaseModel):
    """
    Position Key
    """

    model_config = ConfigDict(frozen=True)

    fen: str = Field(
        description="FEN string representing the chess position",
        min_length=20,
        max_length=100,
    )

    @cached_property
    def trace(self) -> dict[str, str]:
        """
        Trace representation of the position key
        """
        return {
            "fen": self.fen,
        }

    @cached_property
    def safe_string(self) -> str:
        """
        Safe string representation of the position key
        """
        return safe_string(self.trace)
