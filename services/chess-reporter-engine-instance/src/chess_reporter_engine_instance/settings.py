"""
Engine instance: settings module.

All configuration is read from environment variables at startup.
Set them in the Dockerfile / docker-compose / k8s manifest.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Engine instance configuration.

    Environment variables (all optional — defaults shown):
        ENGINE_THREADS: Number of CPU threads for Stockfish (default: 1)
        ENGINE_HASH_MB: Hash table size in megabytes (default: 64)
        ENGINE_DEPTH: Search depth (default: 15)
        ENGINE_MULTIPV: Number of principal variations (default: 3)
        ENGINE_WDL_MODEL: WDL model to use (default: "sf16")
        ENGINE_INSTANCE: Engine instance number (default: 1)
        LOG_LEVEL: Logging level (default: "INFO")
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="ENGINE_",
        case_sensitive=False,
    )

    engine_threads: int = 1
    engine_hash_mb: int = 64
    engine_depth: int = 15
    engine_multipv: int = 3
    engine_wdl_model: str = "sf16"
    engine_instance: int = 1

    log_level: str = "INFO"
