"""
Schemas: Engine response module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .engine_payload import EnginePayload


class EngineResponse(BaseModel):
    """
    Engine Response
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    fen: str = Field(
        description="FEN string representing the chess position",
    )
    status: str = Field(
        description="Status of the engine response (e.g., 'success', 'failure')",
    )
    payload: list[EnginePayload] | None = Field(
        default=None,
        description=(
            "List of engine payloads containing analysis, variation, telemetry,"
            " and tracing data for the position. None while analysis is in progress."
        ),
    )
