"""
Engine instance: setup module.

Entry point for uvicorn. Configures the environment (logger, etc.)
before exposing the FastAPI app.

Run with:
    uvicorn chess_reporter_engine_instance.setup:app --host 0.0.0.0 --port 1999
"""

from __future__ import annotations

import sys

from loguru import logger

from .settings import Settings

_settings: Settings = Settings()

logger.remove()
logger.add(
    sys.stdout,
    level=_settings.log_level,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

from .main import app  # noqa: E402

__all__ = ["app"]
