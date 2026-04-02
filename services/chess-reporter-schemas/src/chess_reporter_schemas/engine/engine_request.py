"""
Schemas: Engine request module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EngineRequest(BaseModel):
    """
    Engine Request
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    fen: str = Field(
        description="FEN string representing the chess position",
    )
