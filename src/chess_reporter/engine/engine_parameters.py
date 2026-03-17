"""
Engine package: parameters module
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from chess_reporter.utils.find_engine import find_engine


class EngineParameters(BaseModel):
    """
    Engine Parameters
    """

    path: str = Field(
        description="The path to the engine executable",
        default_factory=find_engine,
        frozen=True,
    )
    threads: int = Field(
        description="Number of threads configured",
        default=4,
        ge=1,
        frozen=True,
    )
    hash_table_mb: int = Field(
        description="Size of the hash table in megabytes",
        default=4096,
        ge=64,
        frozen=True,
    )
    depth: int = Field(
        description="Search depth",
        default=30,
        ge=15,
        frozen=True,
    )
    multipv: int = Field(
        description="Number of principal variations to calculate",
        default=7,
        ge=3,
        frozen=True,
    )
    analyses: int = Field(
        description="Number of analysis runs to perform",
        default=7,
        ge=3,
        frozen=True,
    )
    parallelism: bool = Field(
        description="Whether to enable parallelism for the analyses or run in series",
        default=True,
        frozen=True,
    )
    engine_config_table: str = Field(
        description="The full name of the engine configuration table in the database",
        default="chess_reporter.engine_config",
        frozen=True,
    )

    @field_validator("analyses")
    @classmethod
    def validate_analyses(cls, value: int) -> int:
        """
        Validates that the number of principal variations is an odd number.
        """
        if value % 2 == 0:
            raise ValueError("analyses must be odd")

        return value

    @property
    def config_mapping(self) -> dict[str, str | int | bool]:
        """
        Converts the engine parameters to a ConfigMapping for configuring the engine.
        """
        return {
            "Threads": self.threads,
            "Hash": self.hash_table_mb,
        }
