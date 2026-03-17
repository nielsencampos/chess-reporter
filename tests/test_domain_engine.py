"""
Tests for domain/engine: EngineConfigData, EngineContext, EngineEvaluationType,
EngineScoreType, EngineAnalysis, and builder functions.
"""

from __future__ import annotations

from datetime import datetime, timezone

from chess import WHITE, Board, Move
from chess.engine import Cp, Mate, PovScore
from pytest import raises

from chess_reporter.domain.engine import (
    EngineAnalysis,
    EngineContext,
    EngineEvaluationType,
    EngineScoreType,
)
from chess_reporter.domain.engine.build_engine_refutation_moves import (
    build_engine_refutation_moves,
)
from chess_reporter.domain.engine.build_engine_variation_moves import (
    build_engine_variation_moves,
)
from chess_reporter.domain.game import GameOutcome, GameResult, GameTermination
from chess_reporter.domain.move import MoveContext
from chess_reporter.domain.position import PositionContext
from chess_reporter.engine.engine_config_data import EngineConfigData

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCHOLARS_MATE_FEN: str = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"


def _make_context(board: Board, run: int = 1) -> EngineContext:
    return EngineContext(
        position_context=PositionContext(board=board),
        analysis_run=run,
    )


def _make_analysis(board: Board, info: dict, run: int = 1) -> EngineAnalysis:  # type: ignore[type-arg]
    return EngineAnalysis(
        context=_make_context(board, run),
        started_analysis_at=datetime.now(timezone.utc),
        info_dict=info,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# EngineConfigData
# ---------------------------------------------------------------------------


def test_engine_config_data_valid() -> None:
    """
    A valid EngineConfigData is created with all fields.
    """
    config: EngineConfigData = EngineConfigData(
        name_version="Stockfish 18",
        threads=4,
        hash_table_mb=4096,
        depth=30,
        multipv=7,
        analyses=7,
        parallelism=True,
    )

    assert config.name_version == "Stockfish 18"
    assert config.threads == 4
    assert config.parallelism is True


def test_engine_config_data_analyses_even_raises() -> None:
    """
    analyses must be odd — even value raises ValidationError.
    """

    with raises(Exception):
        EngineConfigData(
            name_version="Stockfish 18",
            threads=4,
            hash_table_mb=4096,
            depth=30,
            multipv=7,
            analyses=6,
            parallelism=True,
        )


def test_engine_config_data_hash_is_deterministic() -> None:
    """
    The same configuration always produces the same hash ID.
    """
    config_a: EngineConfigData = EngineConfigData(
        name_version="Stockfish 18",
        threads=4,
        hash_table_mb=4096,
        depth=30,
        multipv=7,
        analyses=7,
        parallelism=True,
    )
    config_b: EngineConfigData = EngineConfigData(
        name_version="Stockfish 18",
        threads=4,
        hash_table_mb=4096,
        depth=30,
        multipv=7,
        analyses=7,
        parallelism=True,
    )

    assert config_a.id == config_b.id


def test_engine_config_data_different_parallelism_produces_different_hash() -> None:
    """
    Changing parallelism changes the hash ID.
    """
    config_parallel: EngineConfigData = EngineConfigData(
        name_version="Stockfish 18",
        threads=4,
        hash_table_mb=4096,
        depth=30,
        multipv=7,
        analyses=7,
        parallelism=True,
    )
    config_series: EngineConfigData = EngineConfigData(
        name_version="Stockfish 18",
        threads=4,
        hash_table_mb=4096,
        depth=30,
        multipv=7,
        analyses=7,
        parallelism=False,
    )

    assert config_parallel.id != config_series.id


# ---------------------------------------------------------------------------
# EngineContext
# ---------------------------------------------------------------------------


def test_engine_context_board_is_copy() -> None:
    """
    EngineContext.board is a copy of the position board — mutating it
    does not affect the original.
    """
    board: Board = Board()
    context: EngineContext = _make_context(board)

    context.board.push(Move.from_uci("e2e4"))

    assert board.ply() == 0


def test_engine_context_analysis_run() -> None:
    """
    analysis_run is stored and accessible.
    """
    board: Board = Board()
    context: EngineContext = _make_context(board, run=3)

    assert context.analysis_run == 3


def test_engine_context_game_outcome_delegates_to_position() -> None:
    """
    game_outcome is delegated from the position_context.
    """
    board: Board = Board(SCHOLARS_MATE_FEN)
    context: EngineContext = _make_context(board)

    assert context.game_outcome.is_finished is True


# ---------------------------------------------------------------------------
# EngineEvaluationType
# ---------------------------------------------------------------------------


def test_engine_evaluation_type_values() -> None:
    """
    All three evaluation types exist with the expected string values.
    """
    assert EngineEvaluationType.NORMAL == "normal"
    assert EngineEvaluationType.FAILED == "failed"
    assert EngineEvaluationType.FORCED == "forced"


# ---------------------------------------------------------------------------
# EngineScoreType
# ---------------------------------------------------------------------------


def test_engine_score_type_values() -> None:
    """
    Both score types exist with the expected string values.
    """
    assert EngineScoreType.CENTIPAWNS == "centipawns"
    assert EngineScoreType.MATE == "mate"


# ---------------------------------------------------------------------------
# EngineAnalysis — evaluation_type
# ---------------------------------------------------------------------------


def test_engine_analysis_evaluation_type_normal() -> None:
    """
    A non-finished position with a score is NORMAL.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(50), WHITE), "multipv": 1}
    )

    assert analysis.evaluation_type == EngineEvaluationType.NORMAL


def test_engine_analysis_evaluation_type_failed() -> None:
    """
    A non-finished position with no score is FAILED.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(board, {"multipv": 1})

    assert analysis.evaluation_type == EngineEvaluationType.FAILED


def test_engine_analysis_evaluation_type_forced() -> None:
    """
    A finished position (checkmate) is FORCED.
    """
    board: Board = Board(SCHOLARS_MATE_FEN)
    analysis: EngineAnalysis = _make_analysis(board, {})

    assert analysis.evaluation_type == EngineEvaluationType.FORCED


# ---------------------------------------------------------------------------
# EngineAnalysis — evaluation string
# ---------------------------------------------------------------------------


def test_engine_analysis_evaluation_positive_centipawns() -> None:
    """
    A positive centipawn score formats as +X.XX.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(126), WHITE), "multipv": 1}
    )

    assert analysis.evaluation == "+1.26"


def test_engine_analysis_evaluation_negative_centipawns() -> None:
    """
    A negative centipawn score formats as -X.XX.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(-300), WHITE), "multipv": 1}
    )

    assert analysis.evaluation == "-3.00"


def test_engine_analysis_evaluation_zero_centipawns() -> None:
    """
    A zero centipawn score formats as 0.00.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(0), WHITE), "multipv": 1}
    )

    assert analysis.evaluation == "0.00"


def test_engine_analysis_evaluation_mate_positive() -> None:
    """
    A mate-in-N score for white formats as +#N.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Mate(3), WHITE), "multipv": 1}
    )

    assert analysis.evaluation == "+#3"


def test_engine_analysis_evaluation_mate_negative() -> None:
    """
    Being mated in N (negative mate) formats as -#N.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Mate(-2), WHITE), "multipv": 1}
    )

    assert analysis.evaluation == "-#-2"


def test_engine_analysis_evaluation_white_wins() -> None:
    """
    A finished position where white wins returns '1-0'.
    """
    board: Board = Board(SCHOLARS_MATE_FEN)
    analysis: EngineAnalysis = _make_analysis(board, {})

    assert analysis.evaluation == "1-0"


def test_engine_analysis_evaluation_draw() -> None:
    """
    A finished draw position returns '1/2-1/2'.
    """
    board: Board = Board()
    draw_outcome: GameOutcome = GameOutcome(
        game_result=GameResult.DRAW,
        game_termination=GameTermination.STALEMATE,
    )
    analysis: EngineAnalysis = EngineAnalysis(
        context=EngineContext(
            position_context=PositionContext(board=board, game_outcome_input=draw_outcome),
            analysis_run=1,
        ),
        started_analysis_at=datetime.now(timezone.utc),
        info_dict={},  # type: ignore[arg-type]
    )

    assert analysis.evaluation == "1/2-1/2"


# ---------------------------------------------------------------------------
# EngineAnalysis — score type and centipawn conversion
# ---------------------------------------------------------------------------


def test_engine_analysis_score_type_centipawns() -> None:
    """
    Centipawn score produces CENTIPAWNS score_type.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(50), WHITE), "multipv": 1}
    )

    assert analysis.score_type == EngineScoreType.CENTIPAWNS


def test_engine_analysis_score_type_mate() -> None:
    """
    Mate score produces MATE score_type.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Mate(5), WHITE), "multipv": 1}
    )

    assert analysis.score_type == EngineScoreType.MATE


def test_engine_analysis_score_in_centipawns_normal() -> None:
    """
    score_in_centipawns returns the raw centipawn value for non-mate scores.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(250), WHITE), "multipv": 1}
    )

    assert analysis.score_in_centipawns == 250


def test_engine_analysis_score_in_centipawns_mate() -> None:
    """
    score_in_centipawns for mate-in-N equals mate_in_centipawns - N.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Mate(3), WHITE), "multipv": 1}
    )

    expected: int = analysis.mate_in_centipawns - 3

    assert analysis.score_in_centipawns == expected


# ---------------------------------------------------------------------------
# EngineAnalysis — hash table usage and time
# ---------------------------------------------------------------------------


def test_engine_analysis_hash_table_usage() -> None:
    """
    hash_table_usage converts hashfull (per-mille) to percentage.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(0), WHITE), "hashfull": 500, "multipv": 1}
    )

    assert analysis.hash_table_usage == 50.0


def test_engine_analysis_time_in_seconds() -> None:
    """
    time_in_seconds returns the time field from the info dict.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(0), WHITE), "time": 1.5, "multipv": 1}
    )

    assert analysis.time_in_seconds == 1.5


# ---------------------------------------------------------------------------
# EngineAnalysis — win probability balance
# ---------------------------------------------------------------------------


def test_engine_analysis_win_probability_balance_positive_score() -> None:
    """
    A positive engine score yields a positive win probability balance.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(300), WHITE), "multipv": 1}
    )

    assert analysis.win_probability_balance > 0.0


def test_engine_analysis_win_probability_balance_negative_score() -> None:
    """
    A negative engine score yields a negative win probability balance.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(-300), WHITE), "multipv": 1}
    )

    assert analysis.win_probability_balance < 0.0


# ---------------------------------------------------------------------------
# EngineAnalysis — variation_rank and analysis_run
# ---------------------------------------------------------------------------


def test_engine_analysis_variation_rank() -> None:
    """
    variation_rank reads multipv from the info dict.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(50), WHITE), "multipv": 3}
    )

    assert analysis.variation_rank == 3


def test_engine_analysis_analysis_run() -> None:
    """
    analysis_run delegates to the context.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board, {"score": PovScore(Cp(50), WHITE), "multipv": 1}, run=5
    )

    assert analysis.analysis_run == 5


# ---------------------------------------------------------------------------
# EngineAnalysis — search depth fields
# ---------------------------------------------------------------------------


def test_engine_analysis_search_depth() -> None:
    """
    search_depth and selective_search_depth are read from the info dict.
    """
    board: Board = Board()
    analysis: EngineAnalysis = _make_analysis(
        board,
        {"score": PovScore(Cp(50), WHITE), "depth": 30, "seldepth": 45, "multipv": 1},
    )

    assert analysis.search_depth == 30
    assert analysis.selective_search_depth == 45


# ---------------------------------------------------------------------------
# build_engine_variation_moves
# ---------------------------------------------------------------------------


def test_build_engine_variation_moves_empty() -> None:
    """
    An empty pv list produces an empty result.
    """
    board: Board = Board()
    result: list[MoveContext] = build_engine_variation_moves(board, [])

    assert result == []


def test_build_engine_variation_moves_single_move() -> None:
    """
    A single-move pv produces one MoveContext with correct SAN.
    """
    board: Board = Board()
    moves: list[Move] = [Move.from_uci("e2e4")]
    result: list[MoveContext] = build_engine_variation_moves(board, moves)

    assert len(result) == 1
    assert result[0].move_san == "e4"


def test_build_engine_variation_moves_sequence() -> None:
    """
    A multi-move pv produces MoveContexts with boards that advance correctly.
    """
    board: Board = Board()
    moves: list[Move] = [Move.from_uci("e2e4"), Move.from_uci("e7e5")]
    result: list[MoveContext] = build_engine_variation_moves(board, moves)

    assert len(result) == 2
    assert result[0].move_san == "e4"
    assert result[1].move_san == "e5"
    assert result[1].board_before.ply() == 1


# ---------------------------------------------------------------------------
# build_engine_refutation_moves
# ---------------------------------------------------------------------------


def test_build_engine_refutation_moves_empty() -> None:
    """
    An empty refutation dict produces an empty result.
    """
    board: Board = Board()
    result: list[tuple[MoveContext, list[MoveContext]]] = build_engine_refutation_moves(board, {})

    assert result == []


def test_build_engine_refutation_moves_legal_move() -> None:
    """
    A legal candidate move produces a tuple with its refutation sequence.
    """
    board: Board = Board()
    candidate: Move = Move.from_uci("e2e4")
    refutation: Move = Move.from_uci("e7e5")
    result: list[tuple[MoveContext, list[MoveContext]]] = build_engine_refutation_moves(
        board, {candidate: [refutation]}
    )

    assert len(result) == 1
    move_ctx, refutation_ctxs = result[0]
    assert move_ctx.move_san == "e4"
    assert len(refutation_ctxs) == 1
    assert refutation_ctxs[0].move_san == "e5"


def test_build_engine_refutation_moves_illegal_move_skipped() -> None:
    """
    An illegal candidate move is silently skipped.
    """
    board: Board = Board()
    illegal: Move = Move.from_uci("e1e8")
    result: list[tuple[MoveContext, list[MoveContext]]] = build_engine_refutation_moves(
        board, {illegal: []}
    )

    assert result == []
