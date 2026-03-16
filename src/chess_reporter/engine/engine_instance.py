"""
Engine package: instance module
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING

from chess.engine import INFO_ALL, InfoDict, Limit, SimpleEngine
from loguru import logger

from chess_reporter.domain.engine import EngineAnalysis, EngineContext

from .engine_config_data import EngineConfigData
from .engine_parameters import EngineParameters

if TYPE_CHECKING:
    from loguru import Logger


class EngineInstance:
    """
    Engine Instance
    """

    def __init__(self, context: EngineContext | None = None) -> None:
        """
        Initializes the EngineInstance.

        Args:
            context (EngineContext | None): The context for the chess engine instance.
                If None, default parameters will be used.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: EngineParameters = EngineParameters()
        self._engine: SimpleEngine | None = SimpleEngine.popen_uci(self._parameters.path)
        self._engine.configure(self._parameters.config_mapping)
        self._limit: Limit = Limit(depth=self._parameters.depth)
        self.config_data: EngineConfigData = EngineConfigData(
            name_version=self._engine.id.get("name", "Unknown Engine"),
            threads=self._parameters.threads,
            hash_table_mb=self._parameters.hash_table_mb,
            depth=self._parameters.depth,
            multipv=self._parameters.multipv,
            analyses=self._parameters.analyses,
            in_parallel=self._parameters.parallelism,
        )
        self._context: EngineContext | None = context

        if self._context is None:
            self.close()

            return

    def __enter__(self) -> EngineInstance:
        """
        Enables the use of the EngineInstance as a context manager.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        Ensures that the engine instance process is properly closed when exiting the context.

        Args:
            exc_type (type[BaseException] | None): The type of the exception, if any, that caused
                 the context to be exited.
            exc_value (BaseException | None): The exception instance, if any, that caused the
                context to be exited.
            traceback (TracebackType | None): The traceback object, if any, associated with the
                exception that caused the context to be exited.
        """
        self.close()

        return False

    def _get_normal_analyses(self) -> list[EngineAnalysis]:
        """
        Retrieves the engine analysis result for a given chess position and analysis index.

        Returns:
            list[EngineAnalysis]: The engine analysis result for the given
                position and analysis index.
        """
        if self._engine is None or self._context is None:
            error: str = (
                "Engine instance is not properly initialized. Cannot retrieve analysis results."
            )

            self._logger.error(error)

            raise RuntimeError(error)

        started_analysis_at: datetime = datetime.now(timezone.utc)
        info_dict_list: list[InfoDict] = self._engine.analyse(
            board=self._context.board,
            multipv=self._parameters.multipv,
            limit=self._limit,
            info=INFO_ALL,
        )
        analyses: list[EngineAnalysis] = [
            EngineAnalysis(
                context=self._context,
                started_analysis_at=started_analysis_at,
                info_dict=info_dict,
            )
            for info_dict in info_dict_list
        ]

        return analyses.copy()

    def _get_forced_analyses(self) -> list[EngineAnalysis]:
        """
        Retrieves the engine analysis result for a given chess position and analysis index,
        with forced moves applied.

        Returns:
            list[EngineAnalysis]: The engine analysis result for the given
                position and analysis index, with forced moves applied.
        """
        if self._engine is None or self._context is None:
            error: str = (
                "Engine instance is not properly initialized. Cannot retrieve analysis results."
            )

            self._logger.error(error)

            raise RuntimeError(error)

        started_analysis_at: datetime = datetime.now(timezone.utc)
        analyses: list[EngineAnalysis] = [
            EngineAnalysis(
                context=self._context,
                started_analysis_at=started_analysis_at,
                info_dict={},
            )
        ]

        return analyses.copy()

    def get_analyses(self) -> list[EngineAnalysis]:
        """
        Retrieves the engine analysis result for a given chess position and analysis index,
        applying forced moves if specified in the context.

        Returns:
            list[EngineAnalysis]: The engine analysis result for the given
                position and analysis index, with forced moves applied if specified.
        """
        if self._engine is None or self._context is None:
            error: str = (
                "Engine instance is not properly initialized. Cannot retrieve analysis results."
            )

            self._logger.error(error)

            raise RuntimeError(error)

        if self._context.game_outcome.is_finished:
            return self._get_forced_analyses()

        return self._get_normal_analyses()

    def close(self) -> None:
        """
        Closes the chess engine process and releases any associated resources.
        """
        if self._engine is None:
            return

        try:
            self._engine.quit()
        except Exception:
            pass
        finally:
            self._engine = None
