"""
Chess engine domain definitions for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from chess_reporter.chess_domain.chess_domain import ScoreType
from chess_reporter.utils.utils import generate_hash_id


class ChessEngineData(BaseModel):
    """
    Data class for storing chess engine configuration parameters.
    """

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Name and version of chess engine", min_length=1)
    threads: int = Field(description="Number of threads configured", ge=1)
    hash_table_mb: int = Field(description="Size of the hash table in megabytes", ge=1024)
    depth: int = Field(description="Search depth", ge=1)
    evaluation_runs: int = Field(description="Number of evaluation runs to perform", ge=3)

    @computed_field
    @property
    def chess_engine_id(self) -> str:
        """
        Unique identifier of chess engine (PK)
        """
        values: List[Any] = [
            self.name,
            self.threads,
            self.hash_table_mb,
            self.depth,
            self.evaluation_runs,
        ]

        value: str = generate_hash_id(values)

        return value

    @field_validator("evaluation_runs")
    @classmethod
    def validate_evaluation_runs(cls, value: int) -> int:
        """
        Validates that the number of evaluation runs is an odd number.
        """
        if value % 2 == 0:
            raise ValueError("evaluation_runs must be odd")

        return value


class EnginePositionAnalysisResult(BaseModel):
    """
    Data class for storing the result of a chess engine analysis for a specific position.
    """

    position_analysis_index: int = Field(
        ge=1,
        description="Index of the analysis for the position",
    )
    score_type: ScoreType = Field(
        description="Type of the score: `cp` for centipawns or `mate` for mate in N moves"
    )
    score_value: int = Field(description="Value of the score: centipawns or mate in N moves")
    depth: int = Field(
        description="Search depth at which the chess engine evaluation was performed"
    )
    seldepth: int = Field(
        description="Selective search depth at which the chess engine evaluation was performed"
    )
    time_in_seconds: float = Field(
        description="Time taken in seconds for the chess engine to perform the evaluation"
    )
    is_forced_result: bool = Field(
        description=(
            "Indicates if the score is derived from a forced game result (no engine evaluation)"
        )
    )
    started_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position started"
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position finished"
    )
