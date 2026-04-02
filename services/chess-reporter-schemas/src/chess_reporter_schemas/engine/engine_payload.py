"""
Schemas: Engine payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .engine_analysis_payload import EngineAnalysisPayload
from .engine_telemetry_payload import EngineTelemetryPayload
from .engine_tracing_payload import EngineTracingPayload
from .engine_variation_payload import EngineVariationPayload


class EnginePayload(BaseModel):
    """
    Engine Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    fen: str = Field(
        description="FEN string representing the chess position",
    )
    analysis_run: int = Field(
        description="Analysis run number for which the result is being reported",
        ge=1,
    )
    variation_rank: int = Field(
        description="Variation rank (multipv) for which the result is being reported",
        ge=1,
    )
    analysis: EngineAnalysisPayload = Field(
        description="Analysis data for the position",
    )
    variation: EngineVariationPayload = Field(
        description="Variation data for the analysis",
    )
    telemetry: EngineTelemetryPayload = Field(
        description="Telemetry data for the analysis",
    )
    tracing: EngineTracingPayload = Field(
        description="Tracing data for the analysis",
    )
