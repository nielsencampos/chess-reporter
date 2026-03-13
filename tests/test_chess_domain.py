"""
Tests for chess_domain module.
"""

from __future__ import annotations

from chess import Board
from pytest import raises

from chess_reporter.chess_domain.position_setup import PositionSetup
from chess_reporter.chess_domain.result_type import ResultType
from chess_reporter.chess_domain.termination_type import TerminationType
from chess_reporter.chess_domain.turn_type import TurnType

# ---------------------------------------------------------------------------
# TurnType
# ---------------------------------------------------------------------------


def test_turn_type_opposite_white() -> None:
    """
    Tests that the opposite of WHITE is BLACK.
    """
    assert TurnType.WHITE.opposite == TurnType.BLACK


def test_turn_type_opposite_black() -> None:
    """
    Tests that the opposite of BLACK is WHITE.
    """
    assert TurnType.BLACK.opposite == TurnType.WHITE


def test_turn_type_label_white() -> None:
    """
    Tests that the label for WHITE is correct.
    """
    assert TurnType.WHITE.label == "White to move"


def test_turn_type_label_black() -> None:
    """
    Tests that the label for BLACK is correct.
    """
    assert TurnType.BLACK.label == "Black to move"


# ---------------------------------------------------------------------------
# TerminationType
# ---------------------------------------------------------------------------


def test_termination_ongoing_is_not_finished() -> None:
    """
    Tests that ONGOING is not a finished state.
    """
    assert TerminationType.ONGOING.is_finished is False


def test_termination_checkmate_is_finished() -> None:
    """
    Tests that CHECKMATE is a finished state.
    """
    assert TerminationType.CHECKMATE.is_finished is True


def test_termination_checkmate_has_winner() -> None:
    """
    Tests that CHECKMATE produces a winner.
    """
    assert TerminationType.CHECKMATE.has_winner is True


def test_termination_stalemate_has_no_winner() -> None:
    """
    Tests that STALEMATE produces no winner.
    """
    assert TerminationType.STALEMATE.has_winner is False


def test_termination_stalemate_is_draw() -> None:
    """
    Tests that STALEMATE is a draw.
    """
    assert TerminationType.STALEMATE.is_draw is True


def test_termination_checkmate_is_not_draw() -> None:
    """
    Tests that CHECKMATE is not a draw.
    """
    assert TerminationType.CHECKMATE.is_draw is False


def test_termination_ongoing_is_not_draw() -> None:
    """
    Tests that ONGOING is not a draw.
    """
    assert TerminationType.ONGOING.is_draw is False


# ---------------------------------------------------------------------------
# ResultType
# ---------------------------------------------------------------------------


def test_result_ongoing_is_not_finished() -> None:
    """
    Tests that ONGOING is not a finished result.
    """
    assert ResultType.ONGOING.is_finished is False


def test_result_white_won_is_finished() -> None:
    """
    Tests that WHITE_WON is a finished result.
    """
    assert ResultType.WHITE_WON.is_finished is True


def test_result_white_won_has_winner() -> None:
    """
    Tests that WHITE_WON produces a winner.
    """
    assert ResultType.WHITE_WON.has_winner is True


def test_result_draw_has_no_winner() -> None:
    """
    Tests that DRAW produces no winner.
    """
    assert ResultType.DRAW.has_winner is False


def test_result_draw_is_draw() -> None:
    """
    Tests that DRAW is a draw.
    """
    assert ResultType.DRAW.is_draw is True


def test_result_white_won_is_not_draw() -> None:
    """
    Tests that WHITE_WON is not a draw.
    """
    assert ResultType.WHITE_WON.is_draw is False


# ---------------------------------------------------------------------------
# PositionSetup
# ---------------------------------------------------------------------------


def test_position_setup_ongoing_auto_resolved() -> None:
    """
    Tests that starting position is auto-resolved to ONGOING termination and result.
    """
    board: Board = Board()  # starting position — ongoing
    setup: PositionSetup = PositionSetup(board=board)

    assert setup.termination == TerminationType.ONGOING
    assert setup.result == ResultType.ONGOING


def test_position_setup_turn_white_at_start() -> None:
    """
    Tests that the starting position has WHITE to move.
    """
    board: Board = Board()
    setup: PositionSetup = PositionSetup(board=board)

    assert setup.turn == TurnType.WHITE


def test_position_setup_fen_matches_board() -> None:
    """
    Tests that the FEN stored in PositionSetup matches the board FEN.
    """
    board: Board = Board()
    setup: PositionSetup = PositionSetup(board=board)

    assert setup.fen == board.fen()


def test_position_setup_checkmate_auto_resolved() -> None:
    """
    Tests that Fool's mate is auto-resolved to CHECKMATE with BLACK_WON.
    """
    board: Board = Board()
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        board.push_uci(move)

    setup: PositionSetup = PositionSetup(board=board)

    assert setup.termination == TerminationType.CHECKMATE
    assert setup.result == ResultType.BLACK_WON


def test_position_setup_explicit_params() -> None:
    """
    Tests that explicit termination and result parameters are preserved as-is.
    """
    board: Board = Board()
    setup: PositionSetup = PositionSetup(
        board=board,
        termination_input=TerminationType.RESIGNATION,
        result_input=ResultType.WHITE_WON,
    )

    assert setup.termination == TerminationType.RESIGNATION
    assert setup.result == ResultType.WHITE_WON


def test_position_setup_inconsistent_params_raises() -> None:
    """
    Tests that inconsistent termination and result parameters raise a ValueError.
    """
    board: Board = Board()

    with raises(ValueError):
        PositionSetup(
            board=board,
            termination_input=TerminationType.CHECKMATE,
            result_input=ResultType.DRAW,
        )


def test_position_setup_only_one_param_raises() -> None:
    """
    Tests that providing only one of termination or result parameters raises a ValueError.
    """
    board: Board = Board()

    with raises(ValueError):
        PositionSetup(
            board=board,
            termination_input=TerminationType.CHECKMATE,
        )
