"""
Chess domain definitions for the Chess Reporter application.
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Dict, Optional

from chess import Board, Outcome, Termination
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScoreType(StrEnum):
    """
    Enumeration of score types for chess engine evaluations.

    Values:
        CP: Centipawns score.
        MATE: Mate score.
    """

    CP = "cp"
    MATE = "mate"


class TurnType(StrEnum):
    """
    Enumeration for the turn to move in the chess position, which can be either 'white' or 'black'.

    Values:
        WHITE (str): White to move
        BLACK (str): Black to move

    Properties:
        opposite: The opposite turn to move
        label: Human-readable label for the turn
    """

    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> TurnType:
        """
        The opposite turn to move
        """
        if self == TurnType.WHITE:
            return TurnType.BLACK
        else:
            return TurnType.WHITE

    @property
    def label(self) -> str:
        """
        Human-readable label for the turn
        """
        if self == TurnType.WHITE:
            return "White to move"
        else:
            return "Black to move"


class TerminationType(StrEnum):
    """
    Enumeration for the termination condition of the game for a chess position.

    Values:
        ONGOING (str): Game is ongoing
        ABANDONMENT (str): Game was abandoned
        CHECKMATE (str): Game finished by checkmate
        RESIGNATION (str): Game finished by resignation
        TIMEOUT (str): Game finished by timeout (win)
        VARIANT (str): Game finished by variant rules
        DRAW_BY_AGREEMENT (str): Game ended in a draw by agreement
        TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL (str): Game ended in a draw due to timeout
            and insufficient material
        STALEMATE (str): Game ended in a stalemate
        INSUFFICIENT_MATERIAL (str): Game ended in a draw due to insufficient material
        THREEFOLD_REPETITION (str): Game ended in a draw due to threefold repetition
        FIFTY_MOVES_RULE (str): Game ended in a draw due to the fifty-move rule
        FIVEFOLD_REPETITION (str): Game ended in a draw due to fivefold repetition
        SEVENTYFIVE_MOVES (str): Game ended in a draw due to seventy-five moves rule
        VARIANT_DRAW (str): Game ended in a draw due to variant rules

    Properties:
        is_finished (bool): Indicating if the game finished
        has_winner (bool): Indicating if the game has a winner
        is_draw (bool): Indicating if the game ended in a draw
    """

    ONGOING = "ongoing"
    ABANDONMENT = "abandonment"
    CHECKMATE = "checkmate"
    RESIGNATION = "resignation"
    TIMEOUT = "timeout"
    VARIANT = "variant"
    DRAW_BY_AGREEMENT = "draw_by_agreement"
    TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL = "timeout_draw_by_insufficient_material"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    THREEFOLD_REPETITION = "threefold_repetition"
    FIFTY_MOVES_RULE = "fifty_moves_rule"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    VARIANT_DRAW = "variant_draw"

    @property
    def is_finished(self) -> bool:
        """
        Indicating if the game finished
        """
        return self is not TerminationType.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Indicating if the game has a winner
        """
        return self in {
            TerminationType.ABANDONMENT,
            TerminationType.CHECKMATE,
            TerminationType.RESIGNATION,
            TerminationType.TIMEOUT,
            TerminationType.VARIANT,
        }

    @property
    def is_draw(self) -> bool:
        """
        Indicating if the game ended in a draw
        """
        return self in {
            TerminationType.DRAW_BY_AGREEMENT,
            TerminationType.TIMEOUT_DRAW_BY_INSUFFICIENT_MATERIAL,
            TerminationType.STALEMATE,
            TerminationType.INSUFFICIENT_MATERIAL,
            TerminationType.THREEFOLD_REPETITION,
            TerminationType.FIFTY_MOVES_RULE,
            TerminationType.FIVEFOLD_REPETITION,
            TerminationType.SEVENTYFIVE_MOVES,
            TerminationType.VARIANT_DRAW,
        }


class ResultType(StrEnum):
    """
    Enumeration for the result of the game for a chess position.

    Values:
        ONGOING (str): Indicating that there is no winner or draw yet
        WHITE_WON (str): Represents white player has won the game
        BLACK_WON (str): Represents black player has won the game
        DRAW (str): Indicating that game ended in a draw

    Properties:
        is_finished (bool): Indicating if the game finished
        has_winner (bool): Indicating if the game has a winner
        is_draw (bool): Indicating if the game ended in a draw
    """

    ONGOING = "ongoing"
    WHITE_WON = "white_won"
    BLACK_WON = "black_won"
    DRAW = "draw"

    @property
    def is_finished(self) -> bool:
        """
        Indicating if the game finished
        """
        return self is not ResultType.ONGOING

    @property
    def has_winner(self) -> bool:
        """
        Indicating if the game has a winner
        """
        return self in {ResultType.WHITE_WON, ResultType.BLACK_WON}

    @property
    def is_draw(self) -> bool:
        """
        Indicating if the game ended in a draw
        """
        return self is ResultType.DRAW


class PositionSetup(BaseModel):
    """
    Model representing the setup of a chess position.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    TERMINATION_MAPPING: ClassVar[Dict[Termination, TerminationType]] = {
        Termination.CHECKMATE: TerminationType.CHECKMATE,
        Termination.STALEMATE: TerminationType.STALEMATE,
        Termination.INSUFFICIENT_MATERIAL: TerminationType.INSUFFICIENT_MATERIAL,
        Termination.SEVENTYFIVE_MOVES: TerminationType.SEVENTYFIVE_MOVES,
        Termination.FIVEFOLD_REPETITION: TerminationType.FIVEFOLD_REPETITION,
        Termination.FIFTY_MOVES: TerminationType.FIFTY_MOVES_RULE,
        Termination.THREEFOLD_REPETITION: TerminationType.THREEFOLD_REPETITION,
        Termination.VARIANT_WIN: TerminationType.VARIANT,
        Termination.VARIANT_LOSS: TerminationType.VARIANT,
        Termination.VARIANT_DRAW: TerminationType.VARIANT_DRAW,
    }

    RESULT_MAPPING: ClassVar[Dict[Optional[bool], ResultType]] = {
        None: ResultType.DRAW,
        True: ResultType.WHITE_WON,
        False: ResultType.BLACK_WON,
    }

    board: Board = Field(
        description=("Chess position represented as a Board instance from the python-chess library")
    )
    termination_parameter: Optional[TerminationType] = Field(
        default=None,
        description="Optional externally informed termination status of the position",
    )
    result_parameter: Optional[ResultType] = Field(
        default=None,
        description="Optional externally informed result of the position",
    )

    def _validate_parameter_pairing(self) -> None:
        """
        Ensures termination and result are either both provided or both omitted.
        """
        termination_is_none: bool = self.termination_parameter is None
        result_is_none: bool = self.result_parameter is None

        if termination_is_none != result_is_none:
            raise ValueError(
                "Inconsistent position setup: termination and result must be both set or both None"
            )

    def _resolve_from_board_if_needed(self) -> None:
        """
        Resolves termination and result from the board when they are not provided.
        """
        if self.termination_parameter is not None and self.result_parameter is not None:
            return

        outcome: Optional[Outcome] = self.board.outcome(claim_draw=False)

        if outcome is None:
            self.termination_parameter = TerminationType.ONGOING
            self.result_parameter = ResultType.ONGOING

            return

        termination: Termination = outcome.termination
        winner: Optional[bool] = outcome.winner

        termination_type: Optional[TerminationType] = self.TERMINATION_MAPPING.get(termination)

        if termination_type is None:
            raise ValueError(f"Unsupported termination from python-chess outcome: {termination}")

        result_type: Optional[ResultType] = self.RESULT_MAPPING.get(winner)

        if result_type is None:
            raise ValueError(f"Unsupported winner value from python-chess outcome: {winner}")

        self.termination_parameter = termination_type
        self.result_parameter = result_type

    def _validate_resolved_state(self) -> None:
        """
        Validates the resolved termination and result state.
        """
        if self.termination_parameter is None or self.result_parameter is None:
            raise ValueError("Failed to determine termination and result from the board position")

        if (
            self.termination_parameter.is_finished != self.result_parameter.is_finished
            or self.termination_parameter.has_winner != self.result_parameter.has_winner
            or self.termination_parameter.is_draw != self.result_parameter.is_draw
        ):
            raise ValueError(
                "Inconsistent position setup: termination and result values do not match"
            )

    @model_validator(mode="after")
    def validate_position_setup_consistency(self) -> PositionSetup:
        """
        Validates the consistency of the position setup.
        """
        self._validate_parameter_pairing()
        self._resolve_from_board_if_needed()
        self._validate_resolved_state()

        return self

    @property
    def fen(self) -> str:
        """
        FEN string representing the chess position.
        """
        return self.board.fen()

    @property
    def turn(self) -> TurnType:
        """
        Player to move: white or black.
        """
        return TurnType.WHITE if self.board.turn else TurnType.BLACK

    @property
    def termination(self) -> TerminationType:
        """
        Termination status of the position evaluation.
        """
        if self.termination_parameter is None:
            raise ValueError("Termination for the chess position is not determined in the context.")

        return self.termination_parameter

    @property
    def result(self) -> ResultType:
        """
        Result of the position evaluation.
        """
        if self.result_parameter is None:
            raise ValueError("Result for the chess position is not determined in the context.")

        return self.result_parameter
