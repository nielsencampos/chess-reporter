"""
Engine instance: health router.
"""

from __future__ import annotations

from chess_reporter_schemas.api import APIHealthPayload, APIHealthStatusType
from fastapi import APIRouter
from loguru import logger

from ..core import Core

router: APIRouter = APIRouter()


@router.get("/health", response_model=APIHealthPayload)
def health() -> APIHealthPayload:
    """
    Health check endpoint.
    Attempts to retrieve the engine name and version to verify that the engine instance
    is healthy and can communicate with the engine process.

    Returns:
        APIHealthPayload: An object containing the health status and any warnings.
    """
    logger.info("GET /health")

    result: APIHealthPayload

    try:
        with Core() as core:
            result = core.health()

            logger.debug("GET /health  response={}", result.model_dump())

            return result
    except Exception as error:
        error_message: str = f"Health check failed: {error}"

        logger.error(error_message)

        result = APIHealthPayload(
            status=APIHealthStatusType.ERROR,
            warnings=[error_message],
        )

        logger.debug("GET /health  response={}", result.model_dump())

        return result

    error_message: str = "Health check failed: An unknown error occurred during the health check."

    result = APIHealthPayload(
        status=APIHealthStatusType.ERROR,
        warnings=[error_message],
    )

    logger.debug("GET /health  response={}", result.model_dump())

    return result
