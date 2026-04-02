"""
Engine instance: Build engine analysis payload module
"""

from __future__ import annotations

from typing import cast

from chess import WHITE, Board
from chess.engine import Cp, PovScore, PovWdl, WdlModel
from chess_reporter_schemas.engine import EngineAnalysisPayload, EngineScoreType


def build_engine_analysis_payload(
    fen: str,
    engine_wdl_model: str,
    pov_score: PovScore | None,
    pov_wdl: PovWdl | None,
    search_depth: int,
    selective_search_depth: int,
) -> EngineAnalysisPayload:
    """
    Build engine analysis payload from the given parameters and the engine's info dictionary.

    Args:
        fen (str): FEN string representing the chess position.
        engine_wdl_model (str): WDL model used for calculating winning/drawing/losing probabilities.
        pov_score (PovScore | None): Point of view score from the engine analysis, if available.
        pov_wdl (PovWdl | None): Point of view WDL from the engine analysis, if available.
        search_depth (int): Search depth for the analysis.
        selective_search_depth (int): Selective search depth for the analysis.

    Returns:
        EngineAnalysisPayload: The constructed engine analysis payload.
    """
    if pov_score is None:
        pov_score = PovScore(Cp(0), WHITE)

    if pov_wdl is None:
        pov_wdl = pov_score.wdl(
            model=cast(WdlModel, engine_wdl_model),
            ply=Board(fen).ply(),
        )

    score_type: EngineScoreType = EngineScoreType.MATE if pov_score.is_mate else EngineScoreType.CP
    score_value: int = (
        pov_score.white().mate()  # type: ignore[union-attr]
        if pov_score.is_mate
        else pov_score.white().score()  # type: ignore[union-attr]
    )
    analysis_depth: int = max(search_depth, selective_search_depth)
    white_winning_probability: float = pov_wdl.white().wins / 1000.0
    white_draw_probability: float = pov_wdl.white().draws / 1000.0
    white_losing_probability: float = pov_wdl.white().losses / 1000.0
    black_winning_probability: float = pov_wdl.black().wins / 1000.0
    black_draw_probability: float = pov_wdl.black().draws / 1000.0
    black_losing_probability: float = pov_wdl.black().losses / 1000.0

    return EngineAnalysisPayload(
        score_type=score_type,
        score_value=score_value,
        analysis_depth=analysis_depth,
        white_winning_probability=white_winning_probability,
        white_draw_probability=white_draw_probability,
        white_losing_probability=white_losing_probability,
        black_winning_probability=black_winning_probability,
        black_draw_probability=black_draw_probability,
        black_losing_probability=black_losing_probability,
    )
