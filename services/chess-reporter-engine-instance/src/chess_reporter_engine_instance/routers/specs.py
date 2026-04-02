"""
Engine instance: specs router.
"""

from __future__ import annotations

from chess_reporter_schemas.engine import EngineInstanceSpecsPayload
from fastapi import APIRouter
from loguru import logger

from ..core import Core

router: APIRouter = APIRouter()


@router.get("/specs", response_model=EngineInstanceSpecsPayload)
def specs() -> EngineInstanceSpecsPayload:
    """
    Specifications endpoint.
    Returns the specifications of the engine instance, including the engine name and version,
    number of threads, hash size, search depth, multipv, WDL model, and instance number.

    Returns:
        EngineInstanceSpecsPayload: An object containing the specifications of the engine instance.
    """
    logger.info("GET /specs")

    result: EngineInstanceSpecsPayload

    try:
        with Core() as core:
            result = core.specs()

            logger.debug("GET /specs  response={}", result.model_dump())

            return result
    except Exception as error:
        logger.error(f"Specs check failed: {error}")

        raise

    error_message: str = "Specs check failed: An unknown error occurred."

    logger.error(error_message)

    raise RuntimeError(error_message)
