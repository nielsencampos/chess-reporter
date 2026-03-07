"""
Database configuration parameters for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field


class DatabaseParameters(BaseModel):
    """
    Configuration parameters for the DuckDB database.
    """

    path: Path = Field(
        default=Path("data/database/chess_reporter.duckdb"),
        description="Path to the DuckDB database file",
    )
    threads: int = Field(default=4, description="Number of execution threads for DuckDB")
    memory_limit: str = Field(default="8GB", description="Maximum memory limit for DuckDB")
    default_schema: str = Field(default="src", description="Default schema used by the application")

    @property
    def config(self) -> Dict[str, Any]:
        """
        DuckDB runtime configuration parameters.
        """
        return {"threads": self.threads, "memory_limit": self.memory_limit}


DatabaseParameters.model_rebuild()
