"""
Position manager for the Chess Reporter application.
"""

from __future__ import annotations

from statistics import median
from typing import TYPE_CHECKING, Dict, List, Optional

from chess import Board, Outcome, Termination
from loguru import logger

from chess_reporter.chess_domain.chess_domain import (
    ResultType,
    ScoreType,
    TerminationType,
    TurnType,
)
from chess_reporter.chess_engine.chess_engine_domain import (
    EnginePositionAnalysisResult,
)
from chess_reporter.chess_engine.chess_engine_manager import ChessEngineManager
from chess_reporter.database.database_domain import Query
from chess_reporter.database.database_manager import DatabaseManager
from chess_reporter.position.position_domain import (
    PositionAnalysisContext,
    PositionAnalysisData,
    PositionData,
    PositionMedianScoreResult,
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

    def __init__(
        self,
        chess_engine_manager: ChessEngineManager,
        board: Board,
        termination: Optional[TerminationType] = None,
        result: Optional[ResultType] = None,
    ) -> None:
        """
        Initializes the PositionManager.
        """
        self.__logger: Logger = logger.bind(name="chess-reporter")

        self.chess_engine_manager: ChessEngineManager = chess_engine_manager
        self.parameters: PositionParameters = PositionParameters()
        self.context: PositionAnalysisContext = PositionAnalysisContext(
            chess_engine_id=self.chess_engine_manager.data.chess_engine_id,
            fen=board.copy(stack=False).fen(),
            turn=TurnType.WHITE if board.copy(stack=False).turn else TurnType.BLACK,
            termination=termination,
            result=result,
            board=board.copy(stack=False),
        )

        if self.context.termination is None or self.context.result is None:
            self.__update_termination_and_result__()

        self.__maintain_data__()

    def __update_termination_and_result__(self) -> None:
        """
        Updates the termination and result attributes in the PositionAnalysisContext
        based on the current board state.
        """
        outcome: Optional[Outcome] = self.context.board.copy(stack=False).outcome(claim_draw=False)

        if outcome is None:
            self.context.termination = TerminationType.ONGOING
            self.context.result = ResultType.ONGOING

            return

        termination: Termination = outcome.termination
        winner: Optional[bool] = outcome.winner

        termination_to_termination_type_mapping: Dict[Termination, TerminationType] = {
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

        winner_to_result_type_mapping: Dict[Optional[bool], ResultType] = {
            None: ResultType.DRAW,
            True: ResultType.WHITE_WON,
            False: ResultType.BLACK_WON,
        }

        self.context.termination = termination_to_termination_type_mapping.get(
            termination, TerminationType.ONGOING
        )
        result_if_finished = winner_to_result_type_mapping.get(winner, ResultType.ONGOING)
        self.context.result = (
            result_if_finished if self.context.termination.is_finished else ResultType.ONGOING
        )

    def __get_engine_position_analysis_results__(self) -> List[EnginePositionAnalysisResult]:
        """
        Retrieves the chess engine analysis results for the current chess position in the context.

        Returns:
            List[EnginePositionAnalysisResult]: A list of engine analysis results for the
                current position.
        """

        if self.context.result is None:
            error: str = "Result for the chess position is not determined in the context."

            self.__logger.error(error)

            raise ValueError(error)

        engine_position_analysis_results: List[EnginePositionAnalysisResult] = (
            self.chess_engine_manager.get_engine_position_analysis_results(
                board=self.context.board.copy(stack=False), result=self.context.result
            )
        )

        return engine_position_analysis_results.copy()

    def __get_position_median_score_result__(
        self, engine_position_analysis_results: List[EnginePositionAnalysisResult]
    ) -> PositionMedianScoreResult:
        """
        Calculates the median score result from a list of engine position analysis results.

        Args:
            engine_position_analysis_results (List[EnginePositionAnalysisResult]): A list of
                engine analysis results for a chess position.
        Returns:
            PositionMedianScoreResult: The median score result calculated from the
                engine analysis results.
        """
        quantity_mate_scores: int = len(
            [
                result
                for result in engine_position_analysis_results
                if result.score_type == ScoreType.MATE
            ]
        )
        score_type: ScoreType = ScoreType.MATE if quantity_mate_scores > 1 else ScoreType.CP
        score_values: List[int] = [
            result.score_value
            for result in engine_position_analysis_results
            if result.score_type == score_type
        ]
        score_value: int = int(round(median(score_values), 0))

        median_score: PositionMedianScoreResult = PositionMedianScoreResult(
            score_type=score_type, score_value=score_value
        )

        return median_score

    def __maintain_data__(self) -> None:
        """
        Maintains the chess engine configuration data in the database.
        """
        database_manager: DatabaseManager = DatabaseManager()

        try:
            position_table = self.parameters.position_table_name
            position_analysis_table = self.parameters.position_analysis_table_name
            position_id = self.context.position_id

            position_quantity_sql: str = (
                f"SELECT (COUNT(1)) AS quantity FROM {position_table} "
                f"WHERE position_id = '{position_id}'"
            )
            position_analysis_quantity_sql: str = (
                f"SELECT (COUNT(1)) AS quantity FROM {position_analysis_table} "
                f"WHERE position_id = '{position_id}'"
            )
            position_quantity_query: Query = database_manager.execute(position_quantity_sql)[0]
            position_analysis_quantity_query: Query = database_manager.execute(
                position_analysis_quantity_sql
            )[0]
            position_quantity: int = (
                position_quantity_query.raw_data[0].get("quantity", 0)  # type: ignore
            )
            position_analysis_quantity: int = (
                position_analysis_quantity_query.raw_data[0].get("quantity", 0)  # type: ignore
            )

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
                position_query: Query = database_manager.execute(position_sql)[0]
                position_analysis_query: Query = database_manager.execute(position_analysis_sql)[0]
                self.position_data: PositionData = (
                    PositionData.model_validate(position_query.raw_data[0])  # type: ignore
                )
                self.position_analysis_data: List[PositionAnalysisData] = [
                    PositionAnalysisData.model_validate(position_analysis)
                    for position_analysis in position_analysis_query.raw_data  # type: ignore
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
                database_manager.execute(position_delete_sql)
                database_manager.execute(position_analysis_delete_sql)

                engine_position_analysis_results: List[EnginePositionAnalysisResult] = (
                    self.__get_engine_position_analysis_results__()
                )
                median_score: PositionMedianScoreResult = self.__get_position_median_score_result__(
                    engine_position_analysis_results=(engine_position_analysis_results)
                )
                self.position_data: PositionData = PositionData(
                    position_id=self.context.position_id,
                    chess_engine_id=self.context.chess_engine_id,
                    fen=self.context.fen,
                    turn=self.context.turn,
                    termination=self.context.termination,
                    result=self.context.result,
                    score_type=median_score.score_type,
                    score_value=median_score.score_value,
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

                database_manager.insert(
                    self.parameters.position_table_name, self.position_data.model_dump()
                )
                position_analysis_data_dicts = [
                    data.model_dump() for data in self.position_analysis_data
                ]
                database_manager.insert(
                    self.parameters.position_analysis_table_name, position_analysis_data_dicts
                )
        except Exception as error:
            self.__logger.exception(
                f"Failed to maintain chess engine configuration data in the database: {error}"
            )
            raise
        finally:
            database_manager.close()
