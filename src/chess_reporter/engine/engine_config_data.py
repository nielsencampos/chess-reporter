"""
Engine package: config data module
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from chess_reporter.domain.data import DataStatus
from chess_reporter.utils.generate_hash_id import generate_hash_id


class EngineConfigData(BaseModel):
    """
    Engine Config Data
    """

    model_config = ConfigDict(extra="ignore")

    name_version: str = Field(description="Name and version of engine", min_length=1)
    threads: int = Field(description="Number of threads configured", ge=1)
    hash_table_mb: int = Field(description="Size of the hash table in megabytes", ge=64)
    depth: int = Field(description="Search depth", ge=1)
    multipv: int = Field(description="Number of principal variations to calculate", ge=3)
    analyses: int = Field(description="Number of analysis runs to perform", ge=3)
    in_parallel: bool = Field(
        description="Whether to run multiple analyses in parallel using multiprocessing",
    )
    status: DataStatus = Field(
        description="Status of the engine configuration",
        default=DataStatus.COMPLETED,
        frozen=True,
    )

    @field_validator("analyses")
    @classmethod
    def validate_analyses(cls, value: int) -> int:
        """
        Validates that the number of analyses is an odd number.
        """
        if value % 2 == 0:
            raise ValueError("analyses must be odd")

        return value

    @computed_field
    @property
    def id(self) -> str:
        """
        Unique identifier of engine configuration (PK)
        """
        values: list[Any] = [
            self.name_version,
            self.threads,
            self.hash_table_mb,
            self.depth,
            self.multipv,
            self.analyses,
            self.in_parallel,
        ]

        value: str = generate_hash_id(values)

        return value
