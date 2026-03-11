"""
Position manager for the Chess Reporter application.
"""

from __future__ import annotations

from datetime import datetime
from statistics import median
from typing import TYPE_CHECKING, List

from loguru import logger

from chess_reporter.chess_domain.chess_domain import PositionSetup, ScoreType, TurnType
from chess_reporter.chess_engine.chess_engine_domain import EnginePositionAnalysisResult
from chess_reporter.chess_engine.chess_engine_manager import ChessEngineManager
from chess_reporter.position.position_domain import (
    AggregatedPositionResults,
    PositionAnalysisContext,
    PositionAnalysisData,
    PositionData,
)
from chess_reporter.position.position_parameters import PositionParameters

if TYPE_CHECKING:
    from loguru import Logger


class PositionManager:
    """
    Manages the chess positions.

    Methods:
        get_engine_position_analysis_results: Retrieves the chess engine analysis
            results for a given chess position.
        close: Closes the chess engine process and releases any associated resources.
    """

    def __init__(self, chess_engine_manager: ChessEngineManager, setup: PositionSetup) -> None:
        """
        Initializes the PositionManager.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._setup: PositionSetup = setup
        self.chess_engine_manager: ChessEngineManager = chess_engine_manager
        self.parameters: PositionParameters = PositionParameters()
        self.context: PositionAnalysisContext = PositionAnalysisContext(
            chess_engine_id=self.chess_engine_manager.data.chess_engine_id,
            fen=setup.fen,
            turn=setup.turn,
            termination=setup.termination,
            result=setup.result,
        )

        self._maintain_data()

    def _get_engine_position_analysis_results(self) -> List[EnginePositionAnalysisResult]:
        """
        Retrieves the chess engine analysis results for the current chess position in the context.

        Returns:
            List[EnginePositionAnalysisResult]: A list of engine analysis results for the
                current position.
        """
        engine_position_analysis_results: List[EnginePositionAnalysisResult] = (
            self.chess_engine_manager.get_engine_position_analysis_results(self._setup)
        )

        return engine_position_analysis_results.copy()

    def _aggregate_position_results(
        self, engine_position_analysis_results: List[EnginePositionAnalysisResult]
    ) -> AggregatedPositionResults:
        """
        Calculates the aggregated results from a list of engine position analysis results.

        Args:
            engine_position_analysis_results (List[EnginePositionAnalysisResult]): A list of
                engine analysis results for a chess position.
        Returns:
            AggregatedPositionResults: The aggregated results calculated from the
                engine analysis results.
        """
        quantity_cp_scores: int = len(
            [
                result
                for result in engine_position_analysis_results
                if result.score_type == ScoreType.CP
            ]
        )
        quantity_mate_scores: int = len(
            [
                result
                for result in engine_position_analysis_results
                if result.score_type == ScoreType.MATE
            ]
        )
        median_score_type: ScoreType = ScoreType.MATE if quantity_mate_scores > 1 else ScoreType.CP
        median_score_values: List[int] = [
            result.score_value
            for result in engine_position_analysis_results
            if result.score_type == median_score_type
        ]
        median_score_value: int = int(round(median(median_score_values), 0))
        minimum_score_type: ScoreType = ScoreType.CP if quantity_cp_scores > 0 else ScoreType.MATE
        minimum_score_values: List[int] = [
            result.score_value
            for result in engine_position_analysis_results
            if result.score_type == minimum_score_type
        ]
        is_white: bool = self.context.turn == TurnType.WHITE
        minimum_score_value: int = (
            min(minimum_score_values) if is_white else max(minimum_score_values)
        )
        maximum_score_type: ScoreType = ScoreType.MATE if quantity_mate_scores > 0 else ScoreType.CP
        maximum_score_values: List[int] = [
            result.score_value
            for result in engine_position_analysis_results
            if result.score_type == maximum_score_type
        ]
        maximum_score_value: int = (
            max(maximum_score_values) if is_white else min(maximum_score_values)
        )
        depth_values = [result.depth for result in engine_position_analysis_results]
        median_depth: int = int(round(median(depth_values), 0))
        seldepth_values = [result.seldepth for result in engine_position_analysis_results]
        median_seldepth: int = int(round(median(seldepth_values), 0))
        time_values = [result.time_in_seconds for result in engine_position_analysis_results]
        median_time_in_seconds: float = round(median(time_values), 2)
        minimum_depth: int = min(depth_values)
        minimum_seldepth: int = min(seldepth_values)
        minimum_time_in_seconds: float = min(time_values)
        maximum_depth: int = max(depth_values)
        maximum_seldepth: int = max(seldepth_values)
        maximum_time_in_seconds: float = max(time_values)
        started_at_values = [
            result.started_analysis_at for result in engine_position_analysis_results
        ]
        started_analysis_at: datetime = min(started_at_values)
        finished_at_values = [
            result.finished_analysis_at for result in engine_position_analysis_results
        ]
        finished_analysis_at: datetime = max(finished_at_values)

        aggregated_position_results: AggregatedPositionResults = AggregatedPositionResults(
            median_score_type=median_score_type,
            median_score_value=median_score_value,
            minimum_score_type=minimum_score_type,
            minimum_score_value=minimum_score_value,
            maximum_score_type=maximum_score_type,
            maximum_score_value=maximum_score_value,
            median_depth=median_depth,
            median_seldepth=median_seldepth,
            median_time_in_seconds=median_time_in_seconds,
            minimum_depth=minimum_depth,
            minimum_seldepth=minimum_seldepth,
            minimum_time_in_seconds=minimum_time_in_seconds,
            maximum_depth=maximum_depth,
            maximum_seldepth=maximum_seldepth,
            maximum_time_in_seconds=maximum_time_in_seconds,
            started_analysis_at=started_analysis_at,
            finished_analysis_at=finished_analysis_at,
        )

        return aggregated_position_results

    def _maintain_data(self) -> None:
        """
        Maintains the chess engine configuration data in the database.
        """
        try:
            position_id = self.context.position_id

            position_quantity_sql: str = (
                f"SELECT (COUNT(1)) AS quantity FROM "
                f"{self.parameters.position_table_name} "
                f"WHERE position_id = '{self.context.position_id}'"
            )
            position_analysis_quantity_sql: str = (
                "SELECT (COUNT(1)) AS quantity FROM "
                f"{self.parameters.position_analysis_table_name} "
                f"WHERE position_id = '{self.context.position_id}'"
            )
            position_quantity: int = self.chess_engine_manager.database_manager.query(
                position_quantity_sql
            ).value
            position_analysis_quantity: int = self.chess_engine_manager.database_manager.query(
                position_analysis_quantity_sql
            ).value

            if (
                position_quantity == 1
                and position_analysis_quantity == self.chess_engine_manager.data.evaluation_runs
            ):
                position_table = self.parameters.position_table_name
                position_analysis_table = self.parameters.position_analysis_table_name
                position_id = self.context.position_id
                position_sql: str = (
                    f"SELECT * FROM {position_table} WHERE position_id = '{position_id}'"
                )
                position_analysis_sql: str = (
                    f"SELECT * FROM {position_analysis_table} WHERE position_id = '{position_id}'"
                )
                self.position_data: PositionData = PositionData.model_validate(
                    self.chess_engine_manager.database_manager.query(position_sql).row
                )
                self.position_analysis_data: List[PositionAnalysisData] = [
                    PositionAnalysisData.model_validate(position_analysis)
                    for position_analysis in self.chess_engine_manager.database_manager.query(
                        position_analysis_sql
                    ).raw_data
                ]
            else:
                position_delete_sql: str = (
                    f"DELETE FROM {self.parameters.position_table_name} "
                    f"WHERE position_id = '{self.context.position_id}'"
                )
                position_analysis_delete_sql: str = (
                    f"DELETE FROM {self.parameters.position_analysis_table_name} "
                    f"WHERE position_id = '{self.context.position_id}'"
                )
                self.chess_engine_manager.database_manager.execute(position_delete_sql)
                self.chess_engine_manager.database_manager.execute(position_analysis_delete_sql)

                engine_position_analysis_results: List[EnginePositionAnalysisResult] = (
                    self._get_engine_position_analysis_results()
                )
                median_score: AggregatedPositionResults = self._aggregate_position_results(
                    engine_position_analysis_results=engine_position_analysis_results
                )
                self.position_data: PositionData = PositionData(
                    position_id=self.context.position_id,
                    chess_engine_id=self.context.chess_engine_id,
                    fen=self.context.fen,
                    turn=self.context.turn,
                    termination=self.context.termination,
                    result=self.context.result,
                    median_score_type=median_score.median_score_type,
                    median_score_value=median_score.median_score_value,
                    minimum_score_type=median_score.minimum_score_type,
                    minimum_score_value=median_score.minimum_score_value,
                    maximum_score_type=median_score.maximum_score_type,
                    maximum_score_value=median_score.maximum_score_value,
                    median_depth=median_score.median_depth,
                    median_seldepth=median_score.median_seldepth,
                    median_time_in_seconds=median_score.median_time_in_seconds,
                    minimum_depth=median_score.minimum_depth,
                    minimum_seldepth=median_score.minimum_seldepth,
                    minimum_time_in_seconds=median_score.minimum_time_in_seconds,
                    maximum_depth=median_score.maximum_depth,
                    maximum_seldepth=median_score.maximum_seldepth,
                    maximum_time_in_seconds=median_score.maximum_time_in_seconds,
                    started_analysis_at=median_score.started_analysis_at,
                    finished_analysis_at=median_score.finished_analysis_at,
                )
                self.position_analysis_data: List[PositionAnalysisData] = [
                    PositionAnalysisData(
                        position_id=self.context.position_id,
                        position_analysis_index=engine_position_analysis_result.position_analysis_index,
                        score_type=engine_position_analysis_result.score_type,
                        score_value=engine_position_analysis_result.score_value,
                        depth=engine_position_analysis_result.depth,
                        seldepth=engine_position_analysis_result.seldepth,
                        time_in_seconds=engine_position_analysis_result.time_in_seconds,
                        is_forced_result=engine_position_analysis_result.is_forced_result,
                        started_analysis_at=engine_position_analysis_result.started_analysis_at,
                        finished_analysis_at=engine_position_analysis_result.finished_analysis_at,
                    )
                    for engine_position_analysis_result in engine_position_analysis_results
                ]

                self.chess_engine_manager.database_manager.insert(
                    self.parameters.position_table_name, self.position_data.model_dump()
                )
                position_analysis_data_dicts = [
                    data.model_dump() for data in self.position_analysis_data
                ]
                self.chess_engine_manager.database_manager.insert(
                    self.parameters.position_analysis_table_name, position_analysis_data_dicts
                )
        except Exception as error:
            self._logger.exception(
                f"Failed to maintain chess engine configuration data in the database: {error}"
            )
            raise
