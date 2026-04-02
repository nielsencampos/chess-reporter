"""
Schemas: Engine variation payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EngineVariationPayload(BaseModel):
    """
    Engine Variation Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    variation_moves: list[str] | None = Field(
        description="List of moves in the variation in UCI format",
    )
    refutation_moves: list[tuple[str, list[str]]] | None = Field(
        description=(
            "List of tuples where each tuple contains a refutation move (in UCI format) "
            "and the list of moves in the refutation line (also in UCI format)"
        ),
    )
