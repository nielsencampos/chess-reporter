"""
Tests for domain/position: PositionTurn, PositionMaterialInfo, PositionLegalMoves,
PositionContext, and the three get_position_* builder functions.
"""

from __future__ import annotations

from chess import Board

from chess_reporter.domain.game import (
    GameOutcome,
    GamePhase,
    GameResult,
    GameTermination,
)
from chess_reporter.domain.position import (
    PositionContext,
    PositionLegalMoves,
    PositionMaterialInfo,
    PositionTurn,
)
from chess_reporter.domain.position.get_position_game_outcome_from_board import (
    get_position_game_outcome_from_board,
)
from chess_reporter.domain.position.get_position_legal_moves_from_board import (
    get_position_legal_moves_from_board,
)
from chess_reporter.domain.position.get_position_material_info_from_board import (
    get_position_material_info_from_board,
)

# Scholar's Mate: black is checkmated (white queen on f7)
SCHOLARS_MATE_FEN: str = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"


# ---------------------------------------------------------------------------
# PositionTurn
# ---------------------------------------------------------------------------


def test_position_turn_opposite() -> None:
    """
    WHITE.opposite is BLACK and vice versa.
    """
    assert PositionTurn.WHITE.opposite is PositionTurn.BLACK
    assert PositionTurn.BLACK.opposite is PositionTurn.WHITE


def test_position_turn_label() -> None:
    """
    label returns a human-readable string for each turn.
    """
    assert "White" in PositionTurn.WHITE.label
    assert "Black" in PositionTurn.BLACK.label


def test_position_turn_priority_and_character() -> None:
    """
    WHITE has lower priority than BLACK and distinct characters.
    """
    assert PositionTurn.WHITE.priority < PositionTurn.BLACK.priority
    assert PositionTurn.WHITE.character != PositionTurn.BLACK.character


# ---------------------------------------------------------------------------
# PositionMaterialInfo
# ---------------------------------------------------------------------------


def test_position_material_info_derived_properties() -> None:
    """
    Derived properties compute correctly from base fields.
    """
    info: PositionMaterialInfo = PositionMaterialInfo(
        white_material=3900,
        white_piece_count=16,
        black_material=3900,
        black_piece_count=16,
    )

    assert info.overall_material == 7800
    assert info.overall_piece_count == 32
    assert info.material_balance == 0
    assert info.piece_count_balance == 0


def test_position_material_info_game_phase_opening() -> None:
    """
    32 pieces → OPENING phase.
    """
    info: PositionMaterialInfo = PositionMaterialInfo(
        white_material=3900,
        white_piece_count=16,
        black_material=3900,
        black_piece_count=16,
    )

    assert info.material_game_phase == GamePhase.OPENING


def test_position_material_info_game_phase_middlegame() -> None:
    """
    Between 12 and 25 pieces → MIDDLEGAME phase.
    """
    info: PositionMaterialInfo = PositionMaterialInfo(
        white_material=1500,
        white_piece_count=10,
        black_material=1500,
        black_piece_count=10,
    )

    assert info.material_game_phase == GamePhase.MIDDLEGAME


def test_position_material_info_game_phase_endgame() -> None:
    """
    Fewer than 12 pieces → ENDGAME phase.
    """
    info: PositionMaterialInfo = PositionMaterialInfo(
        white_material=500,
        white_piece_count=3,
        black_material=500,
        black_piece_count=3,
    )

    assert info.material_game_phase == GamePhase.ENDGAME


# ---------------------------------------------------------------------------
# get_position_material_info_from_board
# ---------------------------------------------------------------------------


def test_get_position_material_info_starting_position() -> None:
    """
    Starting position has 3900 material per side and 16 pieces per side.
    """
    board: Board = Board()
    info: PositionMaterialInfo = get_position_material_info_from_board(board)

    assert info.white_material == 3900
    assert info.black_material == 3900
    assert info.white_piece_count == 16
    assert info.black_piece_count == 16
    assert info.overall_piece_count == 32
    assert info.material_balance == 0


# ---------------------------------------------------------------------------
# get_position_legal_moves_from_board
# ---------------------------------------------------------------------------


def test_get_position_legal_moves_starting_position() -> None:
    """
    Starting position has exactly 20 legal moves (16 pawn + 4 knight).
    """
    board: Board = Board()
    legal_moves: PositionLegalMoves = get_position_legal_moves_from_board(board)

    assert legal_moves.count == 20


def test_get_position_legal_moves_no_captures_in_starting_position() -> None:
    """
    No captures are available from the starting position.
    """
    board: Board = Board()
    legal_moves: PositionLegalMoves = get_position_legal_moves_from_board(board)

    assert legal_moves.captures.count == 0
    assert legal_moves.captures_count == 0


# ---------------------------------------------------------------------------
# get_position_game_outcome_from_board
# ---------------------------------------------------------------------------


def test_get_position_game_outcome_ongoing() -> None:
    """
    Starting position yields an ONGOING game outcome.
    """
    board: Board = Board()
    outcome: GameOutcome = get_position_game_outcome_from_board(board)

    assert outcome.is_finished is False
    assert outcome.game_result == GameResult.ONGOING
    assert outcome.game_termination == GameTermination.ONGOING


def test_get_position_game_outcome_checkmate() -> None:
    """
    Scholar's Mate position yields a finished outcome with a winner.
    """
    board: Board = Board(SCHOLARS_MATE_FEN)
    outcome: GameOutcome = get_position_game_outcome_from_board(board)

    assert outcome.is_finished is True
    assert outcome.has_winner is True
    assert outcome.game_termination == GameTermination.CHECKMATE
    assert outcome.game_result == GameResult.WHITE_WON


# ---------------------------------------------------------------------------
# PositionLegalMoves
# ---------------------------------------------------------------------------


def test_position_legal_moves_captures_subset() -> None:
    """
    captures is a subset of all legal moves.
    """
    board: Board = Board()
    legal_moves: PositionLegalMoves = get_position_legal_moves_from_board(board)
    captures: PositionLegalMoves = legal_moves.captures

    assert captures.count <= legal_moves.count


# ---------------------------------------------------------------------------
# PositionContext
# ---------------------------------------------------------------------------


def test_position_context_starting_position_defaults() -> None:
    """
    Default PositionContext (starting board) has expected properties.
    """
    context: PositionContext = PositionContext()

    assert context.turn == PositionTurn.WHITE
    assert context.legal_moves_count == 20
    assert context.white_material == 3900
    assert context.black_material == 3900
    assert context.overall_piece_count == 32
    assert context.material_game_phase == GamePhase.OPENING
    assert context.game_result == GameResult.ONGOING
    assert context.game_termination == GameTermination.ONGOING


def test_position_context_fen() -> None:
    """
    fen property returns the correct FEN string.
    """
    board: Board = Board()
    context: PositionContext = PositionContext(board=board)

    assert context.fen == board.fen()


def test_position_context_ascii_board_non_empty() -> None:
    """
    ascii_board returns a non-empty string representation.
    """
    context: PositionContext = PositionContext()

    assert len(context.ascii_board) > 0


def test_position_context_game_outcome_input_overrides_board() -> None:
    """
    Providing game_outcome_input overrides the board-derived outcome.
    """
    forced_outcome: GameOutcome = GameOutcome(
        game_result=GameResult.DRAW,
        game_termination=GameTermination.AGREEMENT,
    )
    context: PositionContext = PositionContext(game_outcome_input=forced_outcome)

    assert context.game_outcome.game_result == GameResult.DRAW
    assert context.game_outcome.game_termination == GameTermination.AGREEMENT


def test_position_context_checkmate_position() -> None:
    """
    Scholar's Mate position is finished with a winner.
    """
    board: Board = Board(SCHOLARS_MATE_FEN)
    context: PositionContext = PositionContext(board=board)

    assert context.game_result == GameResult.WHITE_WON
    assert context.game_termination == GameTermination.CHECKMATE
    assert context.legal_moves_count == 0
