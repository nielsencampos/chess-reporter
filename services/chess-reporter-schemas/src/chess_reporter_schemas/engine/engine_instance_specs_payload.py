"""
Schemas: Engine instance specifications payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EngineInstanceSpecsPayload(BaseModel):
    """
    Engine Instance Specifications Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name_version: str = Field(
        description="Name and version of the engine",
    )
    threads: int = Field(
        description="Number of threads used by the engine",
    )
    hash_table_mb: int = Field(
        description="Hash size in megabytes",
    )
    depth: int = Field(
        description="Search depth of the engine",
    )
    multipv: int = Field(
        description="Number of principal variations",
    )
    wdl_model: str = Field(
        description="Win/draw/loss model used by the engine",
    )
    instance_number: int = Field(
        description="Instance number of the engine",
    )
