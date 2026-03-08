"""
Chess engine configuration parameters for the Chess Reporter application.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, computed_field, field_validator

from chess_reporter.utils.utils import get_chess_engine_path


class ChessEngineParameters(BaseModel):
    """
    Chess engine configuration parameters for the Chess Reporter application.
    """

    threads: int = Field(
        description="'Number of threads configured",
        default=1,
        ge=1,
        frozen=True,
    )
    hash_table_mb: int = Field(
        description="Size of the hash table in megabytes",
        default=2048,
        ge=1024,
        frozen=True,
    )
    depth: int = Field(
        description="Search depth",
        default=30,
        ge=15,
        frozen=True,
    )
    evaluation_runs: int = Field(
        description="Number of evaluation runs to perform",
        default=5,
        ge=3,
        frozen=True,
    )
    table_name: str = Field(
        description="The name of the database table to store chess engine analysis results",
        default="chess_reporter.chess_engine",
        frozen=True,
    )

    @computed_field
    @property
    def path(self) -> str:
        """
        Current path of the chess engine
        """
        return get_chess_engine_path()

    @field_validator("evaluation_runs")
    @classmethod
    def validate_evaluation_runs(cls, value: int) -> int:
        """
        Validates that the number of evaluation runs is an odd number.
        """
        if value % 2 == 0:
            raise ValueError("evaluation_runs must be odd")

        return value
