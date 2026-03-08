"""
Chess engine manager for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from chess import Board
from chess.engine import INFO_SCORE, InfoDict, Limit, PovScore, Score, SimpleEngine

from chess_reporter.chess_domain.chess_domain import ResultType, ScoreType
from chess_reporter.chess_engine.chess_engine_domain import (
    ChessEngineData,
    EnginePositionAnalysisResult,
)
from chess_reporter.chess_engine.chess_engine_parameters import ChessEngineParameters
from chess_reporter.database.database_domain import Query
from chess_reporter.database.database_manager import DatabaseManager


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
        self.parameters: ChessEngineParameters = ChessEngineParameters()
        self.simple_engine: SimpleEngine = SimpleEngine.popen_uci(self.parameters.path)
        self.simple_engine.configure(
            {"Threads": self.parameters.threads, "Hash": self.parameters.hash_table_mb}
        )
        self.data: ChessEngineData = ChessEngineData(
            name=self.simple_engine.id.get("name", "Unknown Chess Engine"),
            threads=self.parameters.threads,
            hash_table_mb=self.parameters.hash_table_mb,
            depth=self.parameters.depth,
            evaluation_runs=self.parameters.evaluation_runs,
        )
        self.limit: Limit = Limit(depth=self.parameters.depth)

        self.__maintain_data__()

    def __maintain_data__(self) -> None:
        """
        Maintains the chess engine configuration data in the database.
        """
        database_manager: DatabaseManager = DatabaseManager()

        try:
            quantity_sql: str = f"SELECT (COUNT(1)) AS quantity FROM {self.parameters.table_name}"
            quantity_query: Query = database_manager.execute(quantity_sql)[0]
            quantity: int = 0

            if isinstance(quantity_query.raw_data, list) and len(quantity_query.raw_data):
                quantity = quantity_query.raw_data[0].get("quantity", 0)

            if quantity == 0:
                database_manager.insert(self.parameters.table_name, self.data.model_dump())
        except Exception as error:
            raise RuntimeError(
                f"Failed to maintain chess engine configuration data in the database: {error}"
            )
        finally:
            database_manager.close()

    def __get_engine_position_analysis_result__(
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
        if not isinstance(position_analysis_index, int) or position_analysis_index < 1:
            raise ValueError("position_analysis_index must be a positive integer.")

        if not isinstance(board, Board):
            raise TypeError(f"Expected board to be an instance of chess.Board, got {type(board)}")

        started_analysis_at: datetime = datetime.now(timezone.utc)
        pre_engine_position_analysis_result: InfoDict = self.simple_engine.analyse(
            board=board.copy(stack=False), limit=self.limit, info=INFO_SCORE
        )
        pre_pov_score: Optional[PovScore] = pre_engine_position_analysis_result.get("score")

        if not isinstance(pre_pov_score, PovScore):
            raise ValueError("Engine analysis did not return a valid score.")

        pov_score: PovScore = pre_pov_score
        score: Score = pov_score.white()
        score_type: ScoreType = ScoreType.MATE if pov_score.is_mate() else ScoreType.CP
        pre_score_value: Optional[int] = score.mate() if pov_score.is_mate() else score.score()

        if not isinstance(pre_score_value, int):
            raise ValueError("Engine analysis did not return a valid score value.")

        score_value: int = pre_score_value
        depth: int = pre_engine_position_analysis_result.get("depth", self.parameters.depth)
        seldepth: int = pre_engine_position_analysis_result.get("seldepth", self.parameters.depth)
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
        if not isinstance(board, Board):
            raise TypeError(f"Expected board to be an instance of chess.Board, got {type(board)}")

        if not isinstance(result, ResultType):
            raise TypeError(f"Expected result to be an instance of ResultType, got {type(result)}")

        engine_position_analysis_results: List[EnginePositionAnalysisResult] = []

        for position_analysis_index in range(1, self.data.evaluation_runs + 1):
            position_analysis_data: Optional[EnginePositionAnalysisResult] = None
            if result is not ResultType.ONGOING:
                started_analysis_at: datetime = datetime.now(timezone.utc)
                score_type: ScoreType = ScoreType.MATE if result.has_winner else ScoreType.CP
                score_value: int = 0
                depth: int = 0
                seldepth: int = 0
                time_in_seconds: float = 0.0
                ended_analysis_at: datetime = datetime.now(timezone.utc)
                position_analysis_data = EnginePositionAnalysisResult(
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
            else:
                position_analysis_data = self.__get_engine_position_analysis_result__(
                    position_analysis_index=position_analysis_index, board=board.copy(stack=False)
                )

            if position_analysis_data is None:
                raise ValueError("Failed to retrieve engine position analysis result.")

            engine_position_analysis_results.append(position_analysis_data)

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
        self.simple_engine.quit()
