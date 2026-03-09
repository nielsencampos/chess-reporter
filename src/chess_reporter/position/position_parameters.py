"""
Position configuration parameters for the Chess Reporter application.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PositionParameters(BaseModel):
    """
    Position configuration parameters for the Chess Reporter application.
    """

    position_table_name: str = Field(
        description="The name of the database table to store chess position analysis results",
        default="chess_reporter.position",
        frozen=True,
    )
    position_analysis_table_name: str = Field(
        description="The name of the database table to store chess position analysis results",
        default="chess_reporter.position_analysis",
        frozen=True,
    )
