"""
Chess engine instance for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING, Optional

from chess import Board
from chess.engine import INFO_SCORE, InfoDict, Limit, PovScore, Score, SimpleEngine
from loguru import logger

from chess_reporter.chess_domain.chess_domain import ScoreType
from chess_reporter.chess_engine.chess_engine_domain import (
    ChessEngineData,
    EnginePositionAnalysisResult,
)
from chess_reporter.chess_engine.chess_engine_parameters import ChessEngineParameters

if TYPE_CHECKING:
    from loguru import Logger


class ChessEngineInstance:
    """
    Provide the chess engine instance.

    Methods:
        get_engine_position_analysis_results: Retrieves the chess engine analysis
            results for a given chess position.
        close: Closes the chess engine process and releases any associated resources.
    """

    def __init__(self) -> None:
        """
        Initializes the ChessEngineInstance.
        """
        self.__logger: Logger = logger.bind(name="chess-reporter")
        self.__parameters: ChessEngineParameters = ChessEngineParameters()
        self.__simple_engine: SimpleEngine = SimpleEngine.popen_uci(self.__parameters.path)
        self.__simple_engine.configure(
            {"Threads": self.__parameters.threads, "Hash": self.__parameters.hash_table_mb}
        )
        self.data: ChessEngineData = ChessEngineData(
            name=self.__simple_engine.id.get("name", "Unknown Chess Engine"),
            threads=self.__parameters.threads,
            hash_table_mb=self.__parameters.hash_table_mb,
            depth=self.__parameters.depth,
            evaluation_runs=self.__parameters.evaluation_runs,
        )
        self.limit: Limit = Limit(depth=self.__parameters.depth)

    def __enter__(self) -> ChessEngineInstance:
        """
        Enables the use of the ChessEngineInstance as a context manager.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """
        Ensures that the chess engine instance process is properly closed when exiting the context.

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

    def get_engine_position_analysis_result(
        self, position_analysis_index: int, board: Board
    ) -> EnginePositionAnalysisResult:
        """
        Retrieves the chess engine analysis result for a given chess position and analysis index.

        Args:
            position_analysis_index (int): The index of the analysis for the position.
            board (Board): The chess position for which to retrieve the analysis result.

        Returns:
            EnginePositionAnalysisResult: The chess engine analysis result for the given
                position and analysis index.
        """
        started_analysis_at: datetime = datetime.now(timezone.utc)
        pre_engine_position_analysis_result: InfoDict = self.__simple_engine.analyse(
            board=board.copy(stack=False), limit=self.limit, info=INFO_SCORE
        )
        pre_pov_score: Optional[PovScore] = pre_engine_position_analysis_result.get("score")

        if not isinstance(pre_pov_score, PovScore):
            error: str = "Engine analysis did not return a valid score."

            self.__logger.error(error)

            raise ValueError(error)

        pov_score: PovScore = pre_pov_score
        score: Score = pov_score.white()
        score_type: ScoreType = ScoreType.MATE if pov_score.is_mate() else ScoreType.CP
        pre_score_value: Optional[int] = score.mate() if pov_score.is_mate() else score.score()

        if not isinstance(pre_score_value, int):
            error: str = "Engine analysis did not return a valid score value."

            self.__logger.error(error)

            raise ValueError(error)

        score_value: int = pre_score_value
        depth: int = pre_engine_position_analysis_result.get("depth", self.__parameters.depth)
        seldepth: int = pre_engine_position_analysis_result.get("seldepth", self.__parameters.depth)
        time_in_seconds: float = pre_engine_position_analysis_result.get("time", 0.0)
        ended_analysis_at: datetime = datetime.now(timezone.utc)
        engine_position_analysis_result: EnginePositionAnalysisResult = (
            EnginePositionAnalysisResult(
                position_analysis_index=position_analysis_index,
                score_type=score_type,
                score_value=score_value,
                depth=depth,
                seldepth=seldepth,
                time_in_seconds=time_in_seconds,
                is_forced_result=False,
                started_analysis_at=started_analysis_at,
                finished_analysis_at=ended_analysis_at,
            )
        )

        return engine_position_analysis_result

    def close(self) -> None:
        """
        Closes the chess engine process and releases any associated resources.
        """
        self.__simple_engine.quit()
