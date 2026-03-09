"""
Position domain definitions for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from chess import Board
from pydantic import BaseModel, ConfigDict, Field, computed_field

from chess_reporter.chess_domain.chess_domain import (
    ResultType,
    ScoreType,
    TerminationType,
    TurnType,
)
from chess_reporter.utils.utils import generate_hash_id


class PositionAnalysisContext(BaseModel):
    """
    Data class for storing the context of a chess position analysis
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    chess_engine_id: str = Field(
        description="Identifier of the chess engine used for the evaluation (FK)"
    )
    fen: str = Field(description="FEN string representing the chess position")
    turn: TurnType = Field(description="Player to move: `white` or `black`")
    termination: Optional[TerminationType] = Field(
        description="Termination status of the position evaluation"
    )
    result: Optional[ResultType] = Field(description="Result of the position evaluation")
    board: Board = Field(
        description="Chess position represented as a Board instance from the python-chess library"
    )

    @computed_field
    @property
    def position_id(self) -> str:
        """
        Unique identifier of chess position (PK)
        """
        values: List[Any] = [
            self.chess_engine_id,
            self.fen,
            self.turn,
            self.termination,
            self.result,
        ]

        value: str = generate_hash_id(values)

        return value


class PositionMedianScoreResult(BaseModel):
    """
    Data class for storing the median score result of a chess position analysis.
    """

    score_type: ScoreType = Field(
        description="Type of the score: `cp` for centipawns or `mate` for mate in N moves"
    )
    score_value: int = Field(description="Value of the score: centipawns or mate in N moves")


class PositionData(BaseModel):
    """
    Data class for storing the chess position data along with its evaluation results.
    """

    position_id: str = Field(description="Unique identifier of chess position (PK)")
    chess_engine_id: str = Field(
        description="Identifier of the chess engine used for the evaluation (FK)"
    )
    fen: str = Field(description="FEN string representing the chess position")
    turn: TurnType = Field(description="Player to move: `white` or `black`")
    termination: Optional[TerminationType] = Field(
        description="Termination status of the position evaluation"
    )
    result: Optional[ResultType] = Field(description="Result of the position evaluation")
    score_type: ScoreType = Field(
        description="Type of the score: `cp` for centipawns or `mate` for mate in N moves"
    )
    score_value: int = Field(description="Value of the score: centipawns or mate in N moves")


class PositionAnalysisData(BaseModel):
    """
    Data class for storing the chess position analysis data.
    """

    position_id: str = Field(description="Identifier of the chess position being analyzed (FK)")
    position_analysis_index: int = Field(
        ge=1,
        description="Index of the analysis for the position",
    )
    score_type: ScoreType = Field(
        description="Type of the score: `cp` for centipawns or `mate` for mate in N moves"
    )
    score_value: int = Field(description="Value of the score: centipawns or mate in N moves")
    depth: int = Field(
        description="Search depth at which the chess engine evaluation was performed"
    )
    seldepth: int = Field(
        description="Selective search depth at which the chess engine evaluation was performed"
    )
    time_in_seconds: float = Field(
        description="Time taken in seconds for the chess engine to perform the evaluation"
    )
    is_forced_result: bool = Field(
        description=(
            "Indicates if the score is derived from a forced game result (no engine evaluation)"
        )
    )
    started_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position started"
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position finished"
    )

    @computed_field
    @property
    def position_analysis_id(self) -> str:
        """
        Unique identifier of position analysis (PK)
        """
        values: List[Any] = [self.position_id, self.position_analysis_index]

        value: str = generate_hash_id(values)

        return value
