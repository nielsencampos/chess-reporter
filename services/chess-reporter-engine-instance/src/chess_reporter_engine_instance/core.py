"""
Engine instance: core module.

Wraps the engine instance process lifecycle. Configuration is injected via
environment variables at container startup (see settings.py).
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import TracebackType

from chess import Board
from chess.engine import INFO_ALL, InfoDict, Limit, SimpleEngine
from chess_reporter_schemas.api import APIHealthPayload, APIHealthStatusType
from chess_reporter_schemas.engine import EngineInstanceSpecsPayload, EnginePayload
from loguru import logger
from psutil import cpu_percent

from .builders import build_engine_payload
from .settings import Settings
from .utils import find_engine


class Core:
    """
    Thin wrapper around python-chess SimpleEngine.

    Manages the engine instance process lifecycle and exposes a single
    `run(fen)` method that returns raw InfoDict results.
    Configuration is read from environment variables via Settings.
    Intended to be used as a context manager.
    """

    def __init__(self) -> None:
        """
        Opens the engine instance process and applies engine configuration
        from environment variables.
        """
        self._settings: Settings = Settings()
        self._engine: SimpleEngine = SimpleEngine.popen_uci(find_engine())

        self._engine.configure(
            {
                "Threads": self._settings.engine_threads,
                "Hash": self._settings.engine_hash_mb,
            }
        )

        self._name_version: str = self._engine.id.get("name", "Unknown Engine")

    def __enter__(self) -> Core:
        """
        Enables use as a context manager.

        Returns:
            Core: The engine instance itself for use within the context.
        """

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        Ensures the engine instance process is closed on context exit.

        Args:
            exc_type (type[BaseException] | None):
                Exception type if an exception was raised, else None.
            exc_value (BaseException | None):
                Exception instance if an exception was raised, else None.
            traceback (TracebackType | None):
                Traceback if an exception was raised, else None.

        Returns:
            bool: False to propagate exceptions, True to suppress.
        """
        self.close()

        return False

    def _get_info_dict(self, fen: str) -> list[InfoDict]:
        """
        Runs analysis on the given FEN and returns raw InfoDict results.

        Args:
            fen: FEN string representing the chess position to analyze.

        Returns:
            list[InfoDict]: Raw analysis results.
        """
        board: Board = Board(fen)

        info_dicts: list[InfoDict] = self._engine.analyse(
            board=board,
            multipv=self._settings.engine_multipv,
            limit=Limit(depth=self._settings.engine_depth),
            info=INFO_ALL,
        )

        return info_dicts

    def _get_payload(self, fen: str) -> list[EnginePayload]:
        """
        Runs analysis on the given FEN and returns a list of EnginePayloads.

        Args:
            fen: FEN string representing the chess position to analyze.

        Returns:
            list[EnginePayload]: A list of EnginePayloads, one per principal variation (multipv).
        """
        cpu_percent(interval=None)

        started_analysis_at: datetime = datetime.now(UTC)
        info_dicts = self._get_info_dict(fen)
        real_cpu_usage: float = cpu_percent(interval=None)
        engine_payloads: list[EnginePayload] = []

        for info_dict in info_dicts:
            engine_payload: EnginePayload = build_engine_payload(
                engine_wdl_model=self._settings.engine_wdl_model,
                engine_instance=self._settings.engine_instance,
                fen=fen,
                started_analysis_at=started_analysis_at,
                info_dict=info_dict,
                real_cpu_usage=real_cpu_usage,
            )

            engine_payloads.append(engine_payload)

        return engine_payloads

    def health(self) -> APIHealthPayload:
        """
        Performs a health check on the engine instance.

        Returns:
            APIHealthPayload: The health status of the engine instance.
        """
        if self._name_version == "Unknown Engine":
            logger.error("Engine health check failed: Unable to determine engine name and version.")

            return APIHealthPayload(
                status=APIHealthStatusType.WARNING,
                warnings=["Unable to determine engine name and version."],
            )

        return APIHealthPayload(status=APIHealthStatusType.OK)

    def specs(self) -> EngineInstanceSpecsPayload:
        """
        Returns the specifications of the engine instance.

        Returns:
            EngineInstanceSpecsPayload: The specifications of the engine instance.
        """
        return EngineInstanceSpecsPayload(
            name_version=self._name_version,
            threads=self._settings.engine_threads,
            hash_table_mb=self._settings.engine_hash_mb,
            depth=self._settings.engine_depth,
            multipv=self._settings.engine_multipv,
            wdl_model=self._settings.engine_wdl_model,
            instance_number=self._settings.engine_instance,
        )

    def run(self, fen: str) -> list[EnginePayload]:
        """
        Runs analysis on the given FEN and returns a list of EnginePayloads.

        Args:
            fen: FEN string representing the chess position to analyze.

        Returns:
            list[EnginePayload]: A list of EnginePayloads, one per principal variation (multipv).
        """
        logger.info(f"Running engine analysis for FEN: {fen}")

        try:
            payloads: list[EnginePayload] = self._get_payload(fen)

            logger.info(f"Engine analysis completed successfully for FEN: {fen}")

            return payloads
        except Exception as error:
            logger.error(f"Engine analysis failed for FEN: {fen} with error: {error}")

            raise

    def close(self) -> None:
        """
        Quits the engine instance process and releases resources.
        Errors during shutdown are logged.
        """
        try:
            self._engine.quit()
        except Exception as error:
            logger.error(f"Error occurred while closing the engine: {error}")

            raise
