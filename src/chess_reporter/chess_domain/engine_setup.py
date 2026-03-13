"""
Chess domain: Engine setup
"""

from __future__ import annotations

from chess import Board
from pydantic import BaseModel, ConfigDict, Field


class EngineSetup(BaseModel):
    """
    Model representing the setup for chess engine analysis.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position_analysis_index: int = Field(description="Index of the analysis for the position")
    board: Board = Field(
        description="Chess position represented as a Board instance from the python-chess library"
    )
