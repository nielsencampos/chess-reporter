"""
Engine instance: run router.
"""

from __future__ import annotations

from threading import Lock

from chess_reporter_schemas.api import APIResponseStatusType
from chess_reporter_schemas.engine import EnginePayload, EngineRequest, EngineResponse
from fastapi import APIRouter, BackgroundTasks
from loguru import logger

from ..core import Core

router: APIRouter = APIRouter()

_lock: Lock = Lock()
_current_fen: str | None = None
_current_status: APIResponseStatusType | None = None
_current_payloads: list[EnginePayload] | None = None


def _process(fen: str) -> None:
    """
    Runs engine analysis in the background and updates module-level state on completion.

    Sets `_current_status` to COMPLETED on success or FAILED on error.

    Args:
        fen (str): FEN string representing the chess position to analyze.
    """
    global _current_status, _current_payloads

    try:
        with Core() as core:
            result: list[EnginePayload] = core.run(fen)

            with _lock:
                _current_payloads = result
                _current_status = APIResponseStatusType.COMPLETED

        logger.info("Analysis completed for FEN: {}", fen)
    except Exception as error:
        with _lock:
            _current_status = APIResponseStatusType.FAILED

        logger.error("Analysis failed for FEN: {}  error={}", fen, error)


@router.post("/run", response_model=EngineResponse)
def run(request: EngineRequest, background_tasks: BackgroundTasks) -> EngineResponse:
    """
    Accepts, rejects, or returns results for a FEN analysis request.

    - Idle or completed with a new FEN: starts analysis, returns IN_PROGRESS.
    - Completed with the same FEN: returns COMPLETED with payloads.
    - In progress: returns REJECTED.

    Args:
        request: EngineRequest object containing the FEN string to analyze.

    Returns:
        EngineResponse: Current status and payloads (None until completed).
    """
    global _current_fen, _current_status, _current_payloads

    logger.info("POST /run  request={}", request.model_dump_json())

    with _lock:
        if _current_status == APIResponseStatusType.COMPLETED and _current_fen == request.fen:
            assert _current_fen is not None
            return EngineResponse(
                fen=_current_fen,
                status=_current_status,
                payload=_current_payloads,
            )

        accepting: bool = (
            _current_fen is None
            or _current_status == APIResponseStatusType.COMPLETED
            or _current_status == APIResponseStatusType.FAILED
        )

        if accepting:
            _current_fen = request.fen
            _current_status = APIResponseStatusType.IN_PROGRESS
            _current_payloads = None

            background_tasks.add_task(_process, request.fen)

            return EngineResponse(fen=_current_fen, status=_current_status, payload=None)

    logger.warning("POST /run  rejected — instance busy with FEN: {}", _current_fen)

    return EngineResponse(
        fen=_current_fen or "",
        status=APIResponseStatusType.REJECTED,
        payload=None,
    )
