"""
Engine package: manager module
"""

from __future__ import annotations

from queue import Queue
from threading import Event, Lock, Thread
from types import TracebackType
from typing import TYPE_CHECKING

from loguru import logger

from chess_reporter.database import DatabaseManager
from chess_reporter.domain.engine import EngineAnalysis, EngineContext
from chess_reporter.domain.position import PositionContext
from chess_reporter.utils.get_logic_cpu_available import get_logic_cpu_available

from .engine_config_data import EngineConfigData
from .engine_instance import EngineInstance
from .engine_parameters import EngineParameters

if TYPE_CHECKING:
    from loguru import Logger


class EngineManager:
    """
    Engine Manager
    """

    def __init__(self, context: PositionContext) -> None:
        """
        Initializes the EngineManager.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: EngineParameters = EngineParameters()
        self._context: PositionContext = context
        config_data: EngineConfigData | None = None

        with EngineInstance() as instance:
            config_data = instance.config_data

        assert config_data is not None

        self._config_data: EngineConfigData = config_data

        self._save_config_data()

    @property
    def engine_config_id(self) -> str:
        """
        Unique identifier of the engine configuration
        """
        return self._config_data.id

    def __enter__(self) -> EngineManager:
        """
        Enables the use of the EngineManager as a context manager.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        Ensures that the engine manager process is properly closed when exiting the context.

        Args:
            exc_type (type[BaseException] | None): The type of the exception, if any, that caused
                 the context to be exited.
            exc_value (BaseException | None): The exception instance, if any, that caused the
                context to be exited.
            traceback (TracebackType | None): The traceback object, if any, associated with the
                exception that caused the context to be exited.
        """
        return False

    def _save_config_data(self) -> None:
        """
        Saves the engine configuration data in the database.
        """
        with DatabaseManager(internal=True) as database_manager:
            try:
                database_manager.merge(
                    self._config_data.model_dump(mode="json"),
                    self._parameters.engine_config_table,
                )
            except Exception:
                self._logger.exception("Failed to save engine configuration data in the database.")
                raise

        self._logger.info(
            "Engine config data:\n{}",
            self._config_data.model_dump(mode="python"),
        )

    def _get_max_workers(self) -> int:
        """
        Get the maximum number of worker threads to use.

        Returns:
            int: The maximum number of worker threads to use, ensuring at least one thread is always
                available.
        """

        return max(1, get_logic_cpu_available() // self._parameters.threads)

    def _worker(
        self,
        queue: Queue[EngineContext | None],
        results: list[EngineAnalysis],
        lock: Lock,
        stop_event: Event,
    ) -> None:
        """
        Worker function that processes EngineContext items from the queue.

        Args:
            queue (Queue[EngineContext | None]): Queue of contexts to analyze.
            results (list[EngineAnalysis]): Shared list to append results to.
            lock (Lock): Lock protecting the shared results list.
            stop_event (Event): Signals workers to stop after the queue is drained.
        """
        while not stop_event.is_set():
            context: EngineContext | None = queue.get()

            if context is None:
                queue.task_done()
                break

            try:
                with EngineInstance(context) as instance:
                    analyses: list[EngineAnalysis] = instance.get_analyses()

                    with lock:
                        results.extend(analyses)
            finally:
                queue.task_done()

    def _analyze_parallel(self) -> list[EngineAnalysis]:
        """
        Runs the engine analyses in parallel using a worker queue.

        Returns:
            list[EngineAnalysis]: All engine analyses collected across all runs.
        """
        results: list[EngineAnalysis] = []
        lock: Lock = Lock()
        queue: Queue[EngineContext | None] = Queue()
        stop_event: Event = Event()
        max_workers: int = self._get_max_workers()
        threads: list[Thread] = []

        for index in range(max_workers):
            thread: Thread = Thread(
                target=self._worker,
                args=(queue, results, lock, stop_event),
                name=f"engine-worker-{index + 1}",
                daemon=True,
            )
            thread.start()
            threads.append(thread)

        for run in range(1, self._parameters.analyses + 1):
            context: EngineContext = EngineContext(
                position_context=self._context,
                analysis_run=run,
            )
            queue.put(context)

        queue.join()
        stop_event.set()

        for _ in threads:
            queue.put(None)

        for thread in threads:
            thread.join()

        return results

    def _analyze_series(self) -> list[EngineAnalysis]:
        """
        Runs the engine analyses sequentially.

        Returns:
            list[EngineAnalysis]: All engine analyses collected across all runs.
        """
        results: list[EngineAnalysis] = []

        for run in range(1, self._parameters.analyses + 1):
            context: EngineContext = EngineContext(
                position_context=self._context,
                analysis_run=run,
            )

            with EngineInstance(context) as instance:
                results.extend(instance.get_analyses())

        return results

    def analyze(self) -> list[EngineAnalysis]:
        """
        Runs the engine analyses for the stored position context.

        Returns:
            list[EngineAnalysis]: All engine analyses collected across all runs.
        """
        if self._parameters.parallelism:
            return self._analyze_parallel()

        return self._analyze_series()
