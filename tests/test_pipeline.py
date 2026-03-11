"""
Integration tests for the full analysis pipeline:
ChessEngineManager + PositionManager + DatabaseManager.

Both tests require Stockfish (skipped automatically if binary not found).
The 'fast_engine_params' fixture from conftest patches ChessEngineParameters
to use minimum settings (depth=15, evaluation_runs=3) for speed.
"""

from __future__ import annotations

import pytest
from chess import Board

from chess_reporter.chess_domain.chess_domain import (
    PositionSetup,
    ResultType,
    TerminationType,
)
from chess_reporter.chess_engine.chess_engine_manager import ChessEngineManager
from chess_reporter.position.position_manager import PositionManager
from chess_reporter.position.position_parameters import PositionParameters


@pytest.fixture
def engine(db, fast_engine_params):
    """ChessEngineManager wired to the temp DB with fast Stockfish settings."""
    manager = ChessEngineManager()
    yield manager
    manager.close()


# ---------------------------------------------------------------------------
# Checkmate position — engine returns forced result, no Stockfish analysis
# ---------------------------------------------------------------------------


def test_pipeline_checkmate_position_saved(engine) -> None:
    """Fool's mate: full pipeline without actual engine computation."""
    board = Board()
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        board.push_uci(move)

    setup = PositionSetup(board=board)
    pm = PositionManager(chess_engine_manager=engine, setup=setup)

    assert pm.position_data.termination == TerminationType.CHECKMATE
    assert pm.position_data.result == ResultType.BLACK_WON
    assert len(pm.position_analysis_data) == engine.data.evaluation_runs
    assert all(a.is_forced_result for a in pm.position_analysis_data)


def test_pipeline_checkmate_persisted_in_db(engine) -> None:
    """Verifies the position row actually exists in the DB after analysis."""
    board = Board()
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        board.push_uci(move)

    setup = PositionSetup(board=board)
    pm = PositionManager(chess_engine_manager=engine, setup=setup)

    params = PositionParameters()
    q = engine.database_manager.query(
        f"SELECT COUNT(1) AS cnt FROM {params.position_table_name} "
        f"WHERE position_id = '{pm.position_data.position_id}'"
    )
    assert q.value == 1


# ---------------------------------------------------------------------------
# Starting position — Stockfish actually runs
# ---------------------------------------------------------------------------


def test_pipeline_starting_position_analyzed(engine) -> None:
    """Starting board: Stockfish runs and produces centipawn scores."""
    setup = PositionSetup(board=Board())
    pm = PositionManager(chess_engine_manager=engine, setup=setup)

    assert pm.position_data.termination == TerminationType.ONGOING
    assert pm.position_data.result == ResultType.ONGOING
    assert len(pm.position_analysis_data) == engine.data.evaluation_runs
    assert all(not a.is_forced_result for a in pm.position_analysis_data)


def test_pipeline_starting_position_idempotent(engine) -> None:
    """Calling PositionManager twice for the same position reuses the DB row."""
    setup = PositionSetup(board=Board())
    pm1 = PositionManager(chess_engine_manager=engine, setup=setup)
    pm2 = PositionManager(chess_engine_manager=engine, setup=setup)

    assert pm1.position_data.position_id == pm2.position_data.position_id

    params = PositionParameters()
    q = engine.database_manager.query(
        f"SELECT COUNT(1) AS cnt FROM {params.position_table_name} "
        f"WHERE position_id = '{pm1.position_data.position_id}'"
    )
    assert q.value == 1
