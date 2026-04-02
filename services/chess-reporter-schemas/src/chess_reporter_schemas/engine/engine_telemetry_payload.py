"""
Schemas: Engine telemetry payload module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EngineTelemetryPayload(BaseModel):
    """
    Engine Telemetry Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    failed_analysis: bool = Field(
        description="Indicates whether the engine analysis failed for the position",
    )
    search_depth: int = Field(
        description="Search depth for the analysis",
    )
    selective_search_depth: int = Field(
        description="Selective search depth for the analysis",
    )
    total_positions_evaluated: int = Field(
        description="Total positions evaluated during the analysis",
    )
    nodes_per_second: int = Field(
        description="Nodes per second during the analysis",
    )
    effective_branching_factor: float = Field(
        description="Effective branching factor (EBF) for the analysis",
    )
    tablebase_hits: int = Field(
        description="Number of tablebase hits during the analysis",
    )
    hash_table_usage: float = Field(
        description="Hash table usage percentage during the analysis",
    )
    message: str = Field(
        description="Informational message reported by the engine during the search",
    )
    cpu_load: float = Field(
        description="CPU load reported by the engine",
    )
    real_cpu_usage: float = Field(
        description="Real CPU usage percentage measured during the analysis",
    )
    time_in_seconds: float = Field(
        description="Time taken for the analysis in seconds",
    )
    started_analysis_at: datetime = Field(
        description="Timestamp when the analysis started",
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp when the analysis finished",
    )
    raw_info_dict: dict[str, Any] = Field(
        description=(
            "Raw information dictionary containing the analysis results from the engine. "
            "Keys are strings and values can be of any type."
        ),
    )
