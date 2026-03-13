"""
Chess engine instance for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING, Optional

from chess.engine import INFO_SCORE, InfoDict, Limit, PovScore, Score, SimpleEngine
from loguru import logger

from chess_reporter.chess_domain.engine_setup import EngineSetup
from chess_reporter.chess_domain.score_type import ScoreType
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
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: ChessEngineParameters = ChessEngineParameters()
        self._simple_engine: SimpleEngine = SimpleEngine.popen_uci(self._parameters.path)
        self._simple_engine.configure(
            {"Threads": self._parameters.threads, "Hash": self._parameters.hash_table_mb}
        )
        self._limit: Limit = Limit(depth=self._parameters.depth)
        self.data: ChessEngineData = ChessEngineData(
            name=self._simple_engine.id.get("name", "Unknown Chess Engine"),
            threads=self._parameters.threads,
            hash_table_mb=self._parameters.hash_table_mb,
            depth=self._parameters.depth,
            evaluation_runs=self._parameters.evaluation_runs,
        )

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
        self, setup: EngineSetup
    ) -> EnginePositionAnalysisResult:
        """
        Retrieves the chess engine analysis result for a given chess position and analysis index.

        Args:
            setup (EngineSetup): The setup containing the chess position and analysis parameters.

        Returns:
            EnginePositionAnalysisResult: The chess engine analysis result for the given
                position and analysis index.
        """
        started_analysis_at: datetime = datetime.now(timezone.utc)
        pre_engine_position_analysis_result: InfoDict = self._simple_engine.analyse(
            board=setup.board.copy(stack=False), limit=self._limit, info=INFO_SCORE
        )

        pov_score: PovScore = pre_engine_position_analysis_result.get("score")  # type: ignore
        assert isinstance(pov_score, PovScore), f"Expected PovScore, got {type(pov_score)}"

        score: Score = pov_score.white()
        score_type: ScoreType = ScoreType.MATE if pov_score.is_mate() else ScoreType.CP

        score_value: int = score.mate() if pov_score.is_mate() else score.score()  # type: ignore
        assert isinstance(score_value, int), f"Expected int, got {type(score_value)}"

        depth: int = pre_engine_position_analysis_result.get("depth", self._parameters.depth)
        seldepth: int = pre_engine_position_analysis_result.get("seldepth", self._parameters.depth)
        time_in_seconds: float = pre_engine_position_analysis_result.get("time", 0.0)
        ended_analysis_at: datetime = datetime.now(timezone.utc)
        engine_position_analysis_result: EnginePositionAnalysisResult = (
            EnginePositionAnalysisResult(
                position_analysis_index=setup.position_analysis_index,
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
        self._simple_engine.quit()
