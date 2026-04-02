"""
Engine master: request and response schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """
    POST /run request body.
    """

    fen: str = Field(
        description="FEN string representing the chess position to analyze",
    )
    instances: int = Field(
        default=3,
        ge=1,
        le=999,
        description="Number of engine instances to spawn (ports 1001–1999)",
    )
    engine_threads: int = Field(
        default=4,
        ge=1,
        description="Stockfish thread count — also drives CPU request (threads * 1000 + 500)m",
    )
    engine_hash_mb: int = Field(
        default=4096,
        ge=256,
        description=(
            "Stockfish hash table in MB — "
            "container memory = hash_mb + 1024 Mi, /dev/shm = hash_mb Mi"
        ),
    )
    engine_depth: int = Field(
        default=30,
        ge=1,
        le=50,
        description="Search depth",
    )
    engine_multipv: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of principal variations",
    )
    engine_wdl_model: str = Field(
        default="sf16",
        description="WDL model passed to Stockfish",
    )
