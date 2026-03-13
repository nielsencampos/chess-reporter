"""
Position domain definitions for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, Field, computed_field

from chess_reporter.chess_domain.result_type import ResultType
from chess_reporter.chess_domain.score_type import ScoreType
from chess_reporter.chess_domain.termination_type import TerminationType
from chess_reporter.chess_domain.turn_type import TurnType
from chess_reporter.utils.generate_hash_id import generate_hash_id


class PositionAnalysisContext(BaseModel):
    """
    Data class for storing the context of a chess position analysis
    """

    chess_engine_id: str = Field(
        description="Identifier of the chess engine used for the evaluation (FK)"
    )
    fen: str = Field(description="FEN string representing the chess position")
    termination: TerminationType = Field(
        description="Termination status of the position evaluation"
    )
    result: ResultType = Field(description="Result of the position evaluation")
    turn: TurnType = Field(description="Player to move: `white` or `black`")
    chess960: bool = Field(
        description="Flag indicating the position originates from a Chess960 (Fischer Random) game"
    )
    board: str = Field(description="Board string representation of the chess position")

    @computed_field
    @property
    def position_id(self) -> str:
        """
        Unique identifier of chess position (PK)
        """
        values: List[Any] = [
            self.chess_engine_id,
            self.fen,
            self.termination,
            self.result,
        ]

        value: str = generate_hash_id(values)

        return value


class AggregatedPositionResults(BaseModel):
    """
    Data class for storing the aggregated chess position analysis results.
    """

    median_score_type: ScoreType = Field(
        description=(
            "Type of the median and final score: `cp` for centipawns or `mate` for mate in N moves"
        ),
    )
    median_score_value: int = Field(
        description="Value of the median and final score: centipawns or mate in N moves"
    )
    minimum_score_type: ScoreType = Field(
        description="Type of the minimum score: `cp` for centipawns or `mate` for mate in N moves"
    )
    minimum_score_value: int = Field(
        description="Value of the minimum score: centipawns or mate in N moves"
    )
    maximum_score_type: ScoreType = Field(
        description="Type of the maximum score: `cp` for centipawns or `mate` for mate in N moves"
    )
    maximum_score_value: int = Field(
        description="Value of the maximum score: centipawns or mate in N moves"
    )
    median_depth: int = Field(
        description="Median search depth across all evaluations for the position"
    )
    median_seldepth: int = Field(
        description="Median selective search depth across all evaluations for the position"
    )
    median_time_in_seconds: float = Field(
        description="Median time taken in seconds across all evaluations for the position"
    )
    minimum_depth: int = Field(
        description="Minimum search depth across all evaluations for the position"
    )
    minimum_seldepth: int = Field(
        description="Minimum selective search depth across all evaluations for the position"
    )
    minimum_time_in_seconds: float = Field(
        description="Minimum time taken in seconds across all evaluations for the position"
    )
    maximum_depth: int = Field(
        description="Maximum search depth across all evaluations for the position"
    )
    maximum_seldepth: int = Field(
        description="Maximum selective search depth across all evaluations for the position"
    )
    maximum_time_in_seconds: float = Field(
        description="Maximum time taken in seconds across all evaluations for the position"
    )
    started_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position started"
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position finished"
    )


class PositionData(BaseModel):
    """
    Data class for storing the chess position data along with its evaluation results.
    """

    position_id: str = Field(description="Unique identifier of chess position (PK)")
    chess_engine_id: str = Field(
        description="Identifier of the chess engine used for the evaluation (FK)"
    )
    fen: str = Field(description="FEN string representing the chess position")
    termination: TerminationType = Field(
        description="Termination status of the position evaluation"
    )
    result: ResultType = Field(description="Result of the position evaluation")
    turn: TurnType = Field(description="Player to move: `white` or `black`")
    chess960: bool = Field(
        description="Flag indicating the position originates from a Chess960 (Fischer Random) game"
    )
    board: str = Field(description="Board string representation of the chess position")
    median_score_type: ScoreType = Field(
        description=(
            "Type of the median and final score: `cp` for centipawns or `mate` for mate in N moves"
        ),
    )
    median_score_value: int = Field(
        description="Value of the median and final score: centipawns or mate in N moves"
    )
    minimum_score_type: ScoreType = Field(
        description="Type of the minimum score: `cp` for centipawns or `mate` for mate in N moves"
    )
    minimum_score_value: int = Field(
        description="Value of the minimum score: centipawns or mate in N moves"
    )
    maximum_score_type: ScoreType = Field(
        description="Type of the maximum score: `cp` for centipawns or `mate` for mate in N moves"
    )
    maximum_score_value: int = Field(
        description="Value of the maximum score: centipawns or mate in N moves"
    )
    median_depth: int = Field(
        description="Median search depth across all evaluations for the position"
    )
    median_seldepth: int = Field(
        description="Median selective search depth across all evaluations for the position"
    )
    median_time_in_seconds: float = Field(
        description="Median time taken in seconds across all evaluations for the position"
    )
    minimum_depth: int = Field(
        description="Minimum search depth across all evaluations for the position"
    )
    minimum_seldepth: int = Field(
        description="Minimum selective search depth across all evaluations for the position"
    )
    minimum_time_in_seconds: float = Field(
        description="Minimum time taken in seconds across all evaluations for the position"
    )
    maximum_depth: int = Field(
        description="Maximum search depth across all evaluations for the position"
    )
    maximum_seldepth: int = Field(
        description="Maximum selective search depth across all evaluations for the position"
    )
    maximum_time_in_seconds: float = Field(
        description="Maximum time taken in seconds across all evaluations for the position"
    )
    started_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position started"
    )
    finished_analysis_at: datetime = Field(
        description="Timestamp indicating when the chess engine analysis for this position finished"
    )


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
