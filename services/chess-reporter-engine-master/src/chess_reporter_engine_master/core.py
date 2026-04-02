"""
Engine master: core module.

Orchestrates fan-out of analysis requests to engine instances and aggregates results.
Configuration is injected via environment variables at container startup (see settings.py).
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import TracebackType

import httpx
from chess_reporter_schemas.api import APIHealthPayload, APIHealthStatusType
from chess_reporter_schemas.engine import EnginePayload, EngineRequest
from kubernetes import client, config
from loguru import logger

from .settings import Settings


class Core:
    """
    Orchestrates fan-out of analysis requests to engine instances.

    Resolves each instance by its StatefulSet DNS, fans out in parallel,
    and aggregates results. Intended to be used as a context manager.
    """

    def __init__(self) -> None:
        """
        Loads settings from environment variables.
        """
        self._settings: Settings = Settings()

    def __enter__(self) -> Core:
        """
        Enables use as a context manager.

        Returns:
            Core: The core instance itself for use within the context.
        """

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        No-op — no resources to release.

        Returns:
            bool: False to propagate exceptions.
        """

        return False

    def _instance_url(self, index: int) -> str:
        """
        Builds the internal cluster DNS URL for a given instance index.

        Args:
            index (int): StatefulSet pod index (0-based).

        Returns:
            str: Full base URL for the engine instance.
        """
        host: str = (
            f"chess-reporter-engine-instance-{index}"
            f".chess-reporter-engine-instance"
            f".{self._settings.namespace}"
            f".svc.cluster.local"
        )

        return f"http://{host}:1999"

    def _call_instance(self, index: int, fen: str) -> list[EnginePayload]:
        """
        Sends a /run request to a single engine instance and returns its payloads.

        Args:
            index (int): StatefulSet pod index (0-based).
            fen (str): FEN string representing the chess position to analyze.

        Returns:
            list[EnginePayload]: Payloads returned by the instance.
        """
        url: str = f"{self._instance_url(index)}/run"
        request: EngineRequest = EngineRequest(fen=fen)

        with httpx.Client(timeout=300.0) as client:
            response: httpx.Response = client.post(
                url,
                content=request.model_dump_json(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

        return [EnginePayload.model_validate(item) for item in response.json()]

    def health(self) -> APIHealthPayload:
        """
        Pings all engine instances and reports any that are unreachable.

        Returns:
            APIHealthPayload: OK if all instances are healthy, WARNING otherwise.
        """
        warnings: list[str] = []

        for i in range(self._settings.engine_instances):
            url: str = f"{self._instance_url(i)}/health"

            try:
                with httpx.Client(timeout=5.0) as client:
                    response: httpx.Response = client.get(url)
                    response.raise_for_status()
            except Exception as error:
                warnings.append(f"Instance {i} unreachable: {error}")

        if warnings:
            return APIHealthPayload(status=APIHealthStatusType.WARNING, warnings=warnings)

        return APIHealthPayload(status=APIHealthStatusType.OK)

    def run(self, fen: str) -> list[EnginePayload]:
        """
        Fans out analysis to all engine instances in parallel and aggregates results.

        Args:
            fen (str): FEN string representing the chess position to analyze.

        Returns:
            list[EnginePayload]: Combined payloads from all instances.
        """
        payloads: list[EnginePayload] = []

        with ThreadPoolExecutor(max_workers=self._settings.engine_instances) as executor:
            futures = {
                executor.submit(self._call_instance, i, fen): i
                for i in range(self._settings.engine_instances)
            }

            for future in as_completed(futures):
                index: int = futures[future]

                try:
                    result: list[EnginePayload] = future.result()
                    payloads.extend(result)
                except Exception as error:
                    logger.error(f"Instance {index} failed: {error}")

                    raise

        return payloads

    def scale(self, replicas: int) -> None:
        """
        Scales the engine instance StatefulSet to the given number of replicas.

        Args:
            replicas (int): Desired number of replicas.
        """
        config.load_incluster_config()
        apps_v1: client.AppsV1Api = client.AppsV1Api()

        apps_v1.patch_namespaced_stateful_set_scale(
            name="chess-reporter-engine-instance",
            namespace=self._settings.namespace,
            body={"spec": {"replicas": replicas}},
        )

        logger.info(f"StatefulSet scaled to {replicas} replica(s)")

    def wait_for_ready(self, timeout: int = 120, interval: int = 5) -> None:
        """
        Polls each instance's /health endpoint until all are reachable or timeout is reached.

        Args:
            timeout (int): Maximum seconds to wait (default: 120).
            interval (int): Seconds between attempts (default: 5).
        """
        deadline: float = time.monotonic() + timeout

        while time.monotonic() < deadline:
            reachable: int = 0

            for i in range(self._settings.engine_instances):
                url: str = f"{self._instance_url(i)}/health"

                try:
                    with httpx.Client(timeout=3.0) as client_http:
                        response: httpx.Response = client_http.get(url)
                        response.raise_for_status()
                    reachable += 1
                except Exception:
                    pass

            if reachable == self._settings.engine_instances:
                logger.info("All engine instances are ready")

                return

            logger.info(
                f"Waiting for instances — {reachable}/{self._settings.engine_instances} ready"
            )
            time.sleep(interval)

        raise TimeoutError(f"Engine instances not ready after {timeout}s")
