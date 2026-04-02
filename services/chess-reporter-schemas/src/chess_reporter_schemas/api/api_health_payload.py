"""
Schemas: API health payload module
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .api_health_status_type import APIHealthStatusType


class APIHealthPayload(BaseModel):
    """
    API Health Payload
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    status: APIHealthStatusType = Field(
        description="Health status of the API",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of warnings related to the API health",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of errors related to the API health",
    )
