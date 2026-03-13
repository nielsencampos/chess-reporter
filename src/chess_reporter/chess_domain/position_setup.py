"""
Chess domain: Position setup
"""

from __future__ import annotations

from typing import ClassVar, Dict, Optional

from chess import Board, Outcome, Termination
from pydantic import BaseModel, ConfigDict, Field, model_validator

from chess_reporter.chess_domain.result_type import ResultType
from chess_reporter.chess_domain.termination_type import TerminationType
from chess_reporter.chess_domain.turn_type import TurnType


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
    termination_input: Optional[TerminationType] = Field(
        default=None,
        description="Optional externally informed termination status of the position",
    )
    result_input: Optional[ResultType] = Field(
        default=None,
        description="Optional externally informed result of the position",
    )

    def _validate_parameter_pairing(self) -> None:
        """
        Ensures termination and result are either both provided or both omitted.
        """
        termination_is_none: bool = self.termination_input is None
        result_is_none: bool = self.result_input is None

        if termination_is_none != result_is_none:
            raise ValueError(
                "Inconsistent position setup: termination and result must be both set or both None"
            )

    def _resolve_from_board_if_needed(self) -> None:
        """
        Resolves termination and result from the board when they are not provided.
        """
        if self.termination_input is not None and self.result_input is not None:
            return

        outcome: Optional[Outcome] = self.board.outcome(claim_draw=False)

        if outcome is None:
            self.termination_input = TerminationType.ONGOING
            self.result_input = ResultType.ONGOING

            return

        termination: Termination = outcome.termination
        winner: Optional[bool] = outcome.winner

        termination_type: Optional[TerminationType] = self.TERMINATION_MAPPING.get(termination)

        if termination_type is None:
            raise ValueError(f"Unsupported termination from python-chess outcome: {termination}")

        result_type: Optional[ResultType] = self.RESULT_MAPPING.get(winner)

        if result_type is None:
            raise ValueError(f"Unsupported winner value from python-chess outcome: {winner}")

        self.termination_input = termination_type
        self.result_input = result_type

    def _validate_resolved_state(self) -> None:
        """
        Validates the resolved termination and result state.
        """
        if self.termination_input is None or self.result_input is None:
            raise ValueError("Failed to determine termination and result from the board position")

        if (
            self.termination_input.is_finished != self.result_input.is_finished
            or self.termination_input.has_winner != self.result_input.has_winner
            or self.termination_input.is_draw != self.result_input.is_draw
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
    def termination(self) -> TerminationType:
        """
        Termination status of the position evaluation.
        """
        if self.termination_input is None:
            raise ValueError("Termination for the chess position is not determined in the context.")

        return self.termination_input

    @property
    def result(self) -> ResultType:
        """
        Result of the position evaluation.
        """
        if self.result_input is None:
            raise ValueError("Result for the chess position is not determined in the context.")

        return self.result_input

    @property
    def turn(self) -> TurnType:
        """
        Player to move: white or black.
        """
        return TurnType.WHITE if self.board.turn else TurnType.BLACK

    @property
    def chess960(self) -> bool:
        """
        Flag indicating the position originates from a Chess960 (Fischer Random) game.
        """
        return self.board.chess960

    @property
    def board_str(self) -> str:
        """
        Board string representation of the chess position.
        """
        return str(self.board)
