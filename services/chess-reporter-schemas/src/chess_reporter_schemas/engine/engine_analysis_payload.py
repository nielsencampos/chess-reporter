"""
Schemas: Engine analysis payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .engine_score_type import EngineScoreType


class EngineAnalysisPayload(BaseModel):
    """
    Engine Analysis Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    score_type: EngineScoreType = Field(
        description="Type of the engine score (cp or mate)",
    )
    score_value: int = Field(
        description=(
            "Value of the engine score. For cp, it's the centipawn value. "
            "For mate, it's the number of moves until mate (positive for white, negative for black)"
        ),
    )
    analysis_depth: int = Field(
        description="Search depth for the analysis",
    )
    white_winning_probability: float = Field(
        description="Winning probability for white as estimated by the engine in percentage",
    )
    white_draw_probability: float = Field(
        description="Draw probability for white as estimated by the engine in percentage",
    )
    white_losing_probability: float = Field(
        description="Losing probability for white as estimated by the engine in percentage",
    )
    black_winning_probability: float = Field(
        description="Winning probability for black as estimated by the engine in percentage",
    )
    black_draw_probability: float = Field(
        description="Draw probability for black as estimated by the engine in percentage",
    )
    black_losing_probability: float = Field(
        description="Losing probability for black as estimated by the engine in percentage",
    )
