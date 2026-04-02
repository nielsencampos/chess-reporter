"""
Engine master: FastAPI application.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from chess_reporter_schemas.api import APIHealthPayload, APIHealthStatusType
from chess_reporter_schemas.engine import EnginePayload, EngineRequest
from fastapi import FastAPI
from loguru import logger

from .core import Core
from .settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Scales up engine instances on startup and back to zero on shutdown.
    """
    settings: Settings = Settings()

    logger.info(f"Starting up — scaling to {settings.engine_instances} instance(s)")

    with Core() as core:
        core.scale(settings.engine_instances)
        core.wait_for_ready()

    logger.info("All engine instances ready")

    yield

    logger.info("Shutting down — scaling instances to 0")

    with Core() as core:
        core.scale(0)


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="Chess Reporter: Engine Master",
    description=(
        "Orchestrates fan-out of chess position analysis across multiple "
        "engine instances and aggregates the results."
    ),
    version="1.0.0",
)


@app.get("/health", response_model=APIHealthPayload)
def health() -> APIHealthPayload:
    """
    Health check endpoint.
    Pings all engine instances to verify they are reachable and healthy.

    Returns:
        APIHealthPayload: An object containing the health status and any warnings.
    """
    logger.info("GET /health")

    try:
        with Core() as core:
            return core.health()
    except Exception as error:
        error_message: str = f"Health check failed: {error}"

        logger.error(error_message)

        return APIHealthPayload(
            status=APIHealthStatusType.ERROR,
            warnings=[error_message],
        )

    raise RuntimeError("unreachable")


@app.post("/run", response_model=list[EnginePayload])
def run(request: EngineRequest) -> list[EnginePayload]:
    """
    Fans out analysis to all engine instances and aggregates results.

    Args:
        request: EngineRequest object containing the FEN string to analyze.

    Returns:
        list[EnginePayload]: Combined payloads from all engine instances.
    """
    logger.info("POST /run  request={}", request.model_dump_json())

    with Core() as core:
        return core.run(request.fen)

    raise RuntimeError("unreachable")
