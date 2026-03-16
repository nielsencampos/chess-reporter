"""
Tests for domain/game: GameResult, GameTermination, GameOutcome, GamePhase.
"""

from __future__ import annotations

from pytest import raises

from chess_reporter.domain.game import (
    GameOutcome,
    GamePhase,
    GameResult,
    GameTermination,
)

# ---------------------------------------------------------------------------
# GameResult
# ---------------------------------------------------------------------------


def test_game_result_ongoing_is_not_finished() -> None:
    """
    ONGOING is not a finished state.
    """
    result: GameResult = GameResult.ONGOING

    assert result.is_finished is False
    assert result.has_winner is False
    assert result.is_draw is False


def test_game_result_draw() -> None:
    """
    DRAW is finished, has no winner, and is a draw.
    """
    result: GameResult = GameResult.DRAW

    assert result.is_finished is True
    assert result.has_winner is False
    assert result.is_draw is True


def test_game_result_white_won() -> None:
    """
    WHITE_WON is finished and has a winner.
    """
    result: GameResult = GameResult.WHITE_WON

    assert result.is_finished is True
    assert result.has_winner is True
    assert result.is_draw is False


def test_game_result_black_won() -> None:
    """
    BLACK_WON is finished and has a winner.
    """
    result: GameResult = GameResult.BLACK_WON

    assert result.is_finished is True
    assert result.has_winner is True
    assert result.is_draw is False


def test_game_result_character_and_symbol_non_empty() -> None:
    """
    Every GameResult value has a non-empty character and symbol.
    """
    for result in GameResult:
        assert len(result.character) > 0
        assert len(result.symbol) > 0


def test_game_result_priority_ordering() -> None:
    """
    Priority values are unique and positive.
    """
    priorities: list[int] = [r.priority for r in GameResult]

    assert len(priorities) == len(set(priorities))
    assert all(p > 0 for p in priorities)


# ---------------------------------------------------------------------------
# GameTermination
# ---------------------------------------------------------------------------


def test_game_termination_ongoing() -> None:
    """
    ONGOING termination is not finished, not a draw, has no winner.
    """
    termination: GameTermination = GameTermination.ONGOING

    assert termination.is_finished is False
    assert termination.has_winner is False
    assert termination.is_draw is False


def test_game_termination_checkmate_has_winner() -> None:
    """
    CHECKMATE is finished with a winner.
    """
    termination: GameTermination = GameTermination.CHECKMATE

    assert termination.is_finished is True
    assert termination.has_winner is True
    assert termination.is_draw is False


def test_game_termination_stalemate_is_draw() -> None:
    """
    STALEMATE is finished as a draw with no winner.
    """
    termination: GameTermination = GameTermination.STALEMATE

    assert termination.is_finished is True
    assert termination.has_winner is False
    assert termination.is_draw is True


def test_game_termination_draw_values() -> None:
    """
    All draw terminations report is_draw=True.
    """
    draw_terminations: list[GameTermination] = [
        GameTermination.AGREEMENT,
        GameTermination.FIFTY_MOVES_RULE,
        GameTermination.FIVEFOLD_REPETITION,
        GameTermination.INSUFFICIENT_MATERIAL,
        GameTermination.SEVENTYFIVE_MOVES,
        GameTermination.STALEMATE,
        GameTermination.THREEFOLD_REPETITION,
        GameTermination.TIMEOUT_DRAW,
    ]

    for termination in draw_terminations:
        assert termination.is_draw is True
        assert termination.has_winner is False


def test_game_termination_winner_values() -> None:
    """
    All decisive terminations report has_winner=True.
    """
    winner_terminations: list[GameTermination] = [
        GameTermination.ABANDONMENT,
        GameTermination.CHECKMATE,
        GameTermination.FORFEIT,
        GameTermination.RESIGNATION,
        GameTermination.TIMEOUT_WIN,
    ]

    for termination in winner_terminations:
        assert termination.has_winner is True
        assert termination.is_draw is False


# ---------------------------------------------------------------------------
# GameOutcome
# ---------------------------------------------------------------------------


def test_game_outcome_ongoing() -> None:
    """
    Consistent ongoing result+termination creates a valid GameOutcome.
    """
    outcome: GameOutcome = GameOutcome(
        game_result=GameResult.ONGOING,
        game_termination=GameTermination.ONGOING,
    )

    assert outcome.is_finished is False
    assert outcome.has_winner is False
    assert outcome.is_draw is False


def test_game_outcome_checkmate() -> None:
    """
    Consistent checkmate result+termination creates a valid GameOutcome.
    """
    outcome: GameOutcome = GameOutcome(
        game_result=GameResult.WHITE_WON,
        game_termination=GameTermination.CHECKMATE,
    )

    assert outcome.is_finished is True
    assert outcome.has_winner is True
    assert outcome.is_draw is False


def test_game_outcome_draw() -> None:
    """
    Consistent draw result+termination creates a valid GameOutcome.
    """
    outcome: GameOutcome = GameOutcome(
        game_result=GameResult.DRAW,
        game_termination=GameTermination.STALEMATE,
    )

    assert outcome.is_finished is True
    assert outcome.has_winner is False
    assert outcome.is_draw is True


def test_game_outcome_inconsistent_raises() -> None:
    """
    Mixing an ONGOING result with a CHECKMATE termination raises ValueError.
    """
    with raises(Exception):
        GameOutcome(
            game_result=GameResult.ONGOING,
            game_termination=GameTermination.CHECKMATE,
        )


def test_game_outcome_winner_with_draw_termination_raises() -> None:
    """
    Mixing a winning result with a draw termination raises ValueError.
    """
    with raises(Exception):
        GameOutcome(
            game_result=GameResult.WHITE_WON,
            game_termination=GameTermination.STALEMATE,
        )


# ---------------------------------------------------------------------------
# GamePhase
# ---------------------------------------------------------------------------


def test_game_phase_priority_ordering() -> None:
    """
    OPENING < MIDDLEGAME < ENDGAME by priority.
    """
    assert GamePhase.OPENING.priority < GamePhase.MIDDLEGAME.priority
    assert GamePhase.MIDDLEGAME.priority < GamePhase.ENDGAME.priority


def test_game_phase_character_and_symbol_non_empty() -> None:
    """
    Every GamePhase has a non-empty character and symbol.
    """
    for phase in GamePhase:
        assert len(phase.character) > 0
        assert len(phase.symbol) > 0
