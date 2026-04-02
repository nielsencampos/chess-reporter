"""
Schemas: Engine tracing payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EngineTracingPayload(BaseModel):
    """
    Engine Tracing Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    current_move_number: int | None = Field(
        description=(
            "Current move number (currmovenumber) reported by the engine "
            "during the search, if available"
        ),
    )
    current_move: str = Field(
        description=(
            "Current move/UCI (currmove) reported by the engine during the search, if available"
        ),
    )
    current_line_moves: dict[int, list[str]] | None = Field(
        description=(
            "Current line (currline) reported by the engine during the search, if available. "
            "It's a dictionary where the key is the move number and the value is "
            "a list of moves in UCI format, if available"
        ),
    )
