"""
Database package: parameters module
"""

from __future__ import annotations

from os import environ
from pathlib import Path

from pydantic import BaseModel, Field


class DatabaseParameters(BaseModel):
    """
    Database Parameters
    """

    path: Path = Field(
        default_factory=lambda: Path(environ.get("DATABASE_PATH", "data/database/main.duckdb")),
        description="Path to the DuckDB database file",
        frozen=True,
    )
    threads: int = Field(
        default=2,
        description="Number of execution threads for DuckDB",
        frozen=True,
        ge=1,
    )
    memory_limit: str = Field(
        default="2GB",
        description="Maximum memory limit for DuckDB",
        frozen=True,
    )

    @property
    def config(self) -> dict[str, str | bool | int | float | list[str]]:
        """
        DuckDB runtime configuration parameters.
        """
        return {
            "threads": self.threads,
            "memory_limit": self.memory_limit,
            "storage_compatibility_version": "latest",
        }
