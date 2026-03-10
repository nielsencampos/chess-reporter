"""
Chess engine manager for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING, List, Optional

from chess import Board
from loguru import logger

from chess_reporter.chess_domain.chess_domain import ResultType, ScoreType
from chess_reporter.chess_engine.chess_engine_domain import (
    ChessEngineData,
    EnginePositionAnalysisResult,
)
from chess_reporter.chess_engine.chess_engine_instance import ChessEngineInstance
from chess_reporter.chess_engine.chess_engine_parameters import ChessEngineParameters
from chess_reporter.database.database_domain import Query
from chess_reporter.database.database_manager import DatabaseManager

if TYPE_CHECKING:
    from loguru import Logger


class ChessEngineManager:
    """
    Manages the chess engine.

    Methods:
        get_engine_position_analysis_results: Retrieves the chess engine analysis
            results for a given chess position.
        close: Closes the chess engine process and releases any associated resources.
    """

    def __init__(self) -> None:
        """
        Initializes the ChessEngineManager.
        """
        self.__logger: Logger = logger.bind(name="chess-reporter")
        self.parameters: ChessEngineParameters = ChessEngineParameters()
        self.chess_engine_instance: ChessEngineInstance = ChessEngineInstance()
        self.data: ChessEngineData = self.chess_engine_instance.data
        self.database_manager: DatabaseManager = DatabaseManager()

        self.__maintain_data__()

    def __enter__(self) -> ChessEngineManager:
        """
        Enables the use of the ChessEngineManager as a context manager.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """
        Ensures that the chess engine manager process is properly closed when exiting the context.

        Args:
            exc_type: The type of the exception, if any, that caused the
                context to be exited.
            exc_value: The exception instance, if any, that caused the
                context to be exited.
            traceback: The traceback object, if any, associated with the
                exception that caused the context to be exited.
        """
        self.close()

        return False

    def __maintain_data__(self) -> None:
        """
        Maintains the chess engine configuration data in the database.
        """
        try:
            quantity_sql: str = (
                f"SELECT (COUNT(1)) AS quantity FROM {self.parameters.table_name} "
                f"WHERE chess_engine_id = '{self.data.chess_engine_id}'"
            )
            quantity_query: Query = self.database_manager.execute(quantity_sql)[0]
            quantity: int = quantity_query.raw_data[0].get("quantity", 0)  # type: ignore

            if quantity == 0:
                self.database_manager.insert(self.parameters.table_name, self.data.model_dump())
        except Exception as error:
            self.__logger.exception(
                f"Failed to maintain chess engine configuration data in the database: {error}"
            )
            raise

    def get_engine_position_analysis_results(
        self, board: Board, result: ResultType = ResultType.ONGOING
    ) -> List[EnginePositionAnalysisResult]:
        """
        Retrieves the chess engine analysis results for a given chess position.

        Args:
            board (Board): The chess position for which to retrieve the analysis results.
            result (ResultType, optional): The result of the game for the given position.

        Returns:
            List[EnginePositionAnalysisResult]: A list of chess engine analysis
                results for the given position.
        """
        engine_position_analysis_results: List[EnginePositionAnalysisResult] = []

        if result is not ResultType.ONGOING:
            for position_analysis_index in range(1, self.data.evaluation_runs + 1):
                started_analysis_at: datetime = datetime.now(timezone.utc)
                score_type: ScoreType = ScoreType.MATE if result.has_winner else ScoreType.CP
                score_value: int = 0
                depth: int = 0
                seldepth: int = 0
                time_in_seconds: float = 0.0
                ended_analysis_at: datetime = datetime.now(timezone.utc)
                position_analysis_data: EnginePositionAnalysisResult = EnginePositionAnalysisResult(
                    position_analysis_index=position_analysis_index,
                    score_type=score_type,
                    score_value=score_value,
                    depth=depth,
                    seldepth=seldepth,
                    time_in_seconds=time_in_seconds,
                    is_forced_result=True,
                    started_analysis_at=started_analysis_at,
                    finished_analysis_at=ended_analysis_at,
                )
                engine_position_analysis_results.append(position_analysis_data)
        else:
            for position_analysis_index in range(1, self.data.evaluation_runs + 1):
                engine_position_analysis_result: EnginePositionAnalysisResult = (
                    self.chess_engine_instance.get_engine_position_analysis_result(
                        position_analysis_index=position_analysis_index,
                        board=board,
                    )
                )
                engine_position_analysis_results.append(engine_position_analysis_result)

        if len(engine_position_analysis_results) != self.data.evaluation_runs:
            raise ValueError(
                f"Expected {self.data.evaluation_runs} evaluation runs, "
                f"but got {len(engine_position_analysis_results)}"
            )

        return engine_position_analysis_results.copy()

    def close(self) -> None:
        """
        Closes the chess engine process and releases any associated resources.
        """
        self.chess_engine_instance.close()
        self.database_manager.close()
