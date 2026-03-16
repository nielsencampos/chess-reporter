"""
Tests for domain/move: MoveClassification, MoveType, MoveCommentTitle,
MoveCommentElement, MoveComment, MoveContext.
"""

from __future__ import annotations

from chess import Board, Move, parse_square
from pytest import raises

from chess_reporter.domain.move import (
    MoveClassification,
    MoveComment,
    MoveCommentElement,
    MoveCommentTitle,
    MoveContext,
    MoveType,
)

# ---------------------------------------------------------------------------
# MoveClassification
# ---------------------------------------------------------------------------


def test_move_classification_all_values_exist() -> None:
    """
    All 11 classification values are present.
    """
    expected: set[str] = {
        "book",
        "book transposed",
        "blunder",
        "miss",
        "mistake",
        "inaccuracy",
        "forced",
        "good",
        "excellent",
        "great",
        "brilliant",
    }

    assert {c.value for c in MoveClassification} == expected


def test_move_classification_priority_unique() -> None:
    """
    Each classification has a unique priority.
    """
    priorities: list[int] = [c.priority for c in MoveClassification]

    assert len(priorities) == len(set(priorities))


def test_move_classification_character_and_symbol_non_empty() -> None:
    """
    Every classification has a non-empty character and symbol.
    """
    for classification in MoveClassification:
        assert len(classification.character) > 0
        assert len(classification.symbol) > 0


# ---------------------------------------------------------------------------
# MoveType
# ---------------------------------------------------------------------------


def test_move_type_values() -> None:
    """
    All three move types exist.
    """
    assert MoveType.PLAYED == "played"
    assert MoveType.MAINLINE == "mainline"
    assert MoveType.VARIATION == "variation"


def test_move_type_priority_unique() -> None:
    """
    Each move type has a unique priority.
    """
    priorities: list[int] = [t.priority for t in MoveType]

    assert len(priorities) == len(set(priorities))


# ---------------------------------------------------------------------------
# MoveCommentTitle
# ---------------------------------------------------------------------------


def test_move_comment_title_values() -> None:
    """
    All 8 comment titles have the expected string values.
    """
    assert MoveCommentTitle.CLOCK_TIME == "clk"
    assert MoveCommentTitle.ELAPSED_MOVE_TIME == "emt"
    assert MoveCommentTitle.ECO == "eco"
    assert MoveCommentTitle.OPENING == "open"
    assert MoveCommentTitle.GAME_PHASE == "phase"
    assert MoveCommentTitle.EVALUATION == "eval"
    assert MoveCommentTitle.ACCURACY == "acc"
    assert MoveCommentTitle.CLASSIFICATION == "class"


def test_move_comment_title_priority_unique() -> None:
    """
    Each title has a unique priority.
    """
    priorities: list[int] = [t.priority for t in MoveCommentTitle]

    assert len(priorities) == len(set(priorities))


# ---------------------------------------------------------------------------
# MoveCommentElement
# ---------------------------------------------------------------------------


def test_move_comment_element_valid() -> None:
    """
    A valid element is created correctly.
    """
    element: MoveCommentElement = MoveCommentElement(
        title=MoveCommentTitle.EVALUATION,
        content="+1.23",
    )

    assert element.title == MoveCommentTitle.EVALUATION
    assert element.content == "+1.23"


def test_move_comment_element_empty_content_raises() -> None:
    """
    An element with empty content raises a validation error.
    """
    with raises(Exception):
        MoveCommentElement(title=MoveCommentTitle.EVALUATION, content="")


# ---------------------------------------------------------------------------
# MoveComment
# ---------------------------------------------------------------------------


def test_move_comment_parse_pgn_string() -> None:
    """
    A PGN comment string is parsed into MoveCommentElements.
    """
    comment: MoveComment = MoveComment("{[%eval +1.23] [%phase opening]}")  # type: ignore[arg-type]

    assert comment.has(MoveCommentTitle.EVALUATION)
    assert comment.has(MoveCommentTitle.GAME_PHASE)
    assert comment.get(MoveCommentTitle.EVALUATION) == "+1.23"
    assert comment.get(MoveCommentTitle.GAME_PHASE) == "opening"


def test_move_comment_serialize_round_trips() -> None:
    """
    Parsing and re-serializing a PGN comment produces the same structure.
    """
    original: str = "{[%eval +1.23] [%phase opening]}"
    comment: MoveComment = MoveComment(original)  # type: ignore[arg-type]
    serialized: str = comment.model_dump()  # type: ignore[assignment]

    reparsed: MoveComment = MoveComment(serialized)  # type: ignore[arg-type]

    assert reparsed.get(MoveCommentTitle.EVALUATION) == "+1.23"
    assert reparsed.get(MoveCommentTitle.GAME_PHASE) == "opening"


def test_move_comment_empty_string_produces_empty_comment() -> None:
    """
    An empty string produces an empty MoveComment.
    """
    comment: MoveComment = MoveComment("")  # type: ignore[arg-type]

    assert len(comment.root) == 0
    assert comment.model_dump() == ""


def test_move_comment_add() -> None:
    """
    Adding a new element works correctly and raises on duplicate.
    """
    comment: MoveComment = MoveComment([])  # type: ignore[arg-type]

    comment.add(MoveCommentTitle.EVALUATION, "+0.50")

    assert comment.has(MoveCommentTitle.EVALUATION)
    assert comment.get(MoveCommentTitle.EVALUATION) == "+0.50"

    with raises(ValueError):
        comment.add(MoveCommentTitle.EVALUATION, "+1.00")


def test_move_comment_set_updates_existing() -> None:
    """
    Setting an existing element updates its content.
    """
    comment: MoveComment = MoveComment("{[%eval +1.23]}")  # type: ignore[arg-type]

    comment.set(MoveCommentTitle.EVALUATION, "+2.00")

    assert comment.get(MoveCommentTitle.EVALUATION) == "+2.00"


def test_move_comment_set_adds_if_missing() -> None:
    """
    Setting a non-existent element adds it.
    """
    comment: MoveComment = MoveComment([])  # type: ignore[arg-type]

    comment.set(MoveCommentTitle.EVALUATION, "+0.00")

    assert comment.has(MoveCommentTitle.EVALUATION)


def test_move_comment_remove() -> None:
    """
    Removing an element works; get returns None afterwards.
    """
    comment: MoveComment = MoveComment("{[%eval +1.23]}")  # type: ignore[arg-type]

    comment.remove(MoveCommentTitle.EVALUATION)

    assert not comment.has(MoveCommentTitle.EVALUATION)
    assert comment.get(MoveCommentTitle.EVALUATION) is None


def test_move_comment_duplicate_titles_raises() -> None:
    """
    Creating a MoveComment with duplicate titles raises a validation error.
    """
    elements: list[MoveCommentElement] = [
        MoveCommentElement(title=MoveCommentTitle.EVALUATION, content="+1.00"),
        MoveCommentElement(title=MoveCommentTitle.EVALUATION, content="+2.00"),
    ]

    with raises(Exception):
        MoveComment(elements)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# MoveContext
# ---------------------------------------------------------------------------


def test_move_context_uci_and_san() -> None:
    """
    MoveContext correctly computes UCI and SAN for 1.e4.
    """
    board: Board = Board()
    move: Move = Move.from_uci("e2e4")
    context: MoveContext = MoveContext(board_before=board, move=move)

    assert context.move_uci == "e2e4"
    assert context.move_san == "e4"


def test_move_context_not_capture() -> None:
    """
    A pawn push from the starting position is not a capture.
    """
    board: Board = Board()
    move: Move = Move.from_uci("e2e4")
    context: MoveContext = MoveContext(board_before=board, move=move)

    assert context.move_is_capture is False
    assert context.move_is_en_passant is False
    assert context.move_is_castling is False
    assert context.move_is_promotion is False


def test_move_context_board_after() -> None:
    """
    board_after reflects the position after the move is played.
    """
    board: Board = Board()
    move: Move = Move.from_uci("e2e4")
    context: MoveContext = MoveContext(board_before=board, move=move)
    board_after: Board = context.board_after

    assert board_after.ply() == 1
    assert board_after.piece_at(parse_square("e4")) is not None


def test_move_context_check_detection() -> None:
    """
    move_is_check is True when the move gives check.
    Scholar's Mate: after Qxf7+, black king is in check (and mated).
    """
    # Position before the mating move: 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6??
    board: Board = Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    move: Move = Move.from_uci("h5f7")
    context: MoveContext = MoveContext(board_before=board, move=move)

    assert context.move_is_check is True
    assert context.move_is_checkmate is True
