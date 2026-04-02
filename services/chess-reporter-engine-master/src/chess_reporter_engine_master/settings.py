"""
Engine master: settings module.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Engine master configuration — defines the rules of the engine analysis process.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="ENGINE_",
        case_sensitive=False,
    )

    engine_threads: int = 4
    engine_hash_mb: int = 4096
    engine_depth: int = 30
    engine_multipv: int = Field(default=3, ge=3)
    engine_wdl_model: str = "sf16"
    engine_instances: int = Field(default=3, ge=3, le=23)

    namespace: str = "chess-reporter"
    instance_image: str = "ghcr.io/nielsencampos/chess-reporter-engine-instance:latest"
    log_level: str = "INFO"
