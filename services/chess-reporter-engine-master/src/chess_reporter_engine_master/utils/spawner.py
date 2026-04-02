"""
Engine master: dynamic instance spawner.

Creates and destroys Deployment + Service pairs for engine instances via the
Kubernetes API. Each instance gets a unique port in the range 1001-1023.
Configuration is injected via environment variables at container startup (see settings.py).
"""

from __future__ import annotations

from time import sleep
from typing import Final

from kubernetes import client, config
from loguru import logger

from chess_reporter_engine_master.settings import Settings

BASE_PORT: Final[int] = 1000
READY_TIMEOUT_SECONDS: Final[int] = 120
POLL_INTERVAL_SECONDS: Final[float] = 2.0


class Spawner:
    """
    Manages the lifecycle of engine instance Deployment + Service pairs in Kubernetes.

    Handles creation, readiness polling, and deletion of Deployment + Service
    pairs for each engine instance. Configuration is read from environment
    variables via Settings. Intended to be used as a context manager.
    """

    def __init__(self) -> None:
        """
        Loads settings and initializes Kubernetes API clients.

        Attempts in-cluster config first, falls back to local kubeconfig.
        """
        self._settings: Settings = Settings()

        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()

        self._apps_api: client.AppsV1Api = client.AppsV1Api()
        self._core_api: client.CoreV1Api = client.CoreV1Api()

    def __enter__(self) -> Spawner:
        """
        Enables use as a context manager.

        Returns:
            Spawner: The spawner instance itself for use within the context.
        """

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object,
    ) -> bool:
        """
        No-op — no resources to release on exit.

        Args:
            exc_type (type[BaseException] | None):
                Exception type if an exception was raised, else None.
            exc_value (BaseException | None):
                Exception instance if an exception was raised, else None.
            traceback (object):
                Traceback if an exception was raised, else None.

        Returns:
            bool: False to propagate exceptions.
        """

        return False

    def _instance_name(self, instance_num: int) -> str:
        """
        Returns the Kubernetes resource name for the given instance number.

        Args:
            instance_num (int): Instance number.

        Returns:
            str: Resource name in the form `chess-reporter-engine-instance-{instance_num}`.
        """

        return f"chess-reporter-engine-instance-{instance_num}"

    def _instance_port(self, instance_num: int) -> int:
        """
        Returns the port assigned to the given instance number.

        Args:
            instance_num (int): Instance number.

        Returns:
            int: Port number in the range 1001–1023.
        """

        return BASE_PORT + instance_num

    def _instance_url(self, instance_num: int) -> str:
        """
        Returns the in-cluster base URL for the given instance number.

        Args:
            instance_num (int): Instance number.

        Returns:
            str: Base URL in the form `http://{name}.{namespace}.svc.cluster.local:{port}`.
        """

        name: str = self._instance_name(instance_num)
        port: int = self._instance_port(instance_num)

        return f"http://{name}.{self._settings.namespace}.svc.cluster.local:{port}"

    def _cpu_request(self, engine_threads: int) -> str:
        """
        Returns the CPU resource request string for the given thread count.

        Allocates 1000m per thread plus 500m headroom.

        Args:
            engine_threads (int): Number of engine threads.

        Returns:
            str: CPU request in millicores (e.g. `"4500m"` for 4 threads).
        """

        return f"{engine_threads * 1000 + 500}m"

    def _memory_request(self, engine_hash_mb: int) -> str:
        """
        Returns the memory resource request string for the given hash table size.

        Adds 1024 Mi overhead on top of the hash table size.

        Args:
            engine_hash_mb (int): Hash table size in MB.

        Returns:
            str: Memory request in mebibytes (e.g. `"5120Mi"` for 4096 MB hash).
        """

        return f"{engine_hash_mb + 1024}Mi"

    def _shm_size(self, engine_hash_mb: int) -> str:
        """
        Returns the `/dev/shm` size limit string for the given hash table size.

        Args:
            engine_hash_mb (int): Hash table size in MB.

        Returns:
            str: Shared memory size limit in mebibytes (e.g. `"4096Mi"`).
        """

        return f"{engine_hash_mb}Mi"

    def create(
        self,
        instance_num: int,
        engine_threads: int,
        engine_hash_mb: int,
        engine_depth: int,
        engine_multipv: int,
        engine_wdl_model: str,
    ) -> str:
        """
        Creates a Deployment and Service for the given engine instance.

        Engine configuration is injected as environment variables into the
        container. CPU and memory requests are derived from `engine_threads`
        and `engine_hash_mb`. The instance is not ready to serve traffic
        until `wait_for_ready` returns.

        Args:
            instance_num (int): Instance number, used for naming and port assignment.
            engine_threads (int): Number of CPU threads for the engine.
            engine_hash_mb (int): Hash table size in MB.
            engine_depth (int): Search depth.
            engine_multipv (int): Number of principal variations.
            engine_wdl_model (str): WDL model identifier.

        Returns:
            str: In-cluster base URL of the created instance.
        """
        name: str = self._instance_name(instance_num)
        port: int = self._instance_port(instance_num)
        cpu: str = self._cpu_request(engine_threads)
        memory: str = self._memory_request(engine_hash_mb)
        shm: str = self._shm_size(engine_hash_mb)

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name, namespace=self._settings.namespace),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": name}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": name}),
                    spec=client.V1PodSpec(
                        image_pull_secrets=[client.V1LocalObjectReference(name="ghcr-secret")],
                        containers=[
                            client.V1Container(
                                name=name,
                                image=self._settings.instance_image,
                                ports=[client.V1ContainerPort(container_port=port)],
                                env=[
                                    client.V1EnvVar(
                                        name="ENGINE_INSTANCE",
                                        value=str(instance_num),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_PORT",
                                        value=str(port),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_THREADS",
                                        value=str(engine_threads),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_HASH_MB",
                                        value=str(engine_hash_mb),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_DEPTH",
                                        value=str(engine_depth),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_MULTIPV",
                                        value=str(engine_multipv),
                                    ),
                                    client.V1EnvVar(
                                        name="ENGINE_WDL_MODEL",
                                        value=engine_wdl_model,
                                    ),
                                ],
                                liveness_probe=client.V1Probe(
                                    http_get=client.V1HTTPGetAction(path="/health", port=port),
                                    initial_delay_seconds=5,
                                    period_seconds=10,
                                ),
                                readiness_probe=client.V1Probe(
                                    http_get=client.V1HTTPGetAction(path="/health", port=port),
                                    initial_delay_seconds=5,
                                    period_seconds=5,
                                ),
                                resources=client.V1ResourceRequirements(
                                    requests={"cpu": cpu, "memory": memory},
                                    limits={"cpu": cpu, "memory": memory},
                                ),
                                volume_mounts=[
                                    client.V1VolumeMount(name="dshm", mount_path="/dev/shm"),
                                ],
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="dshm",
                                empty_dir=client.V1EmptyDirVolumeSource(
                                    medium="Memory",
                                    size_limit=shm,
                                ),
                            )
                        ],
                    ),
                ),
            ),
        )

        service = client.V1Service(
            metadata=client.V1ObjectMeta(name=name, namespace=self._settings.namespace),
            spec=client.V1ServiceSpec(
                selector={"app": name},
                ports=[client.V1ServicePort(port=port, target_port=port)],
            ),
        )

        self._apps_api.create_namespaced_deployment(
            namespace=self._settings.namespace,
            body=deployment,
        )
        self._core_api.create_namespaced_service(
            namespace=self._settings.namespace,
            body=service,
        )

        url: str = self._instance_url(instance_num)

        logger.info("Created instance {} → {}", instance_num, url)

        return url

    def wait_for_ready(self, instance_num: int) -> None:
        """
        Blocks until the instance Deployment reports at least one ready replica.

        Polls every `POLL_INTERVAL_SECONDS` up to `READY_TIMEOUT_SECONDS`.
        Raises `TimeoutError` if the instance does not become ready in time.

        Args:
            instance_num (int): Instance number to wait for.
        """
        name: str = self._instance_name(instance_num)
        elapsed: float = 0.0

        logger.info("Waiting for instance {} to be ready...", instance_num)

        while elapsed < READY_TIMEOUT_SECONDS:
            deployment = self._apps_api.read_namespaced_deployment(
                name=name,
                namespace=self._settings.namespace,
            )
            status = deployment.status  # type: ignore[union-attr]
            ready: int = (status.ready_replicas or 0) if status else 0

            if ready >= 1:
                logger.info("Instance {} is ready.", instance_num)

                return

            sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

        raise TimeoutError(f"Timed out waiting for instance {instance_num} to be ready.")

    def delete(self, instance_num: int) -> None:
        """
        Deletes the Deployment and Service for the given engine instance.

        Errors are logged but not re-raised, so cleanup always completes
        for all instances even if one deletion fails.

        Args:
            instance_num (int): Instance number to delete.
        """
        name: str = self._instance_name(instance_num)

        try:
            self._apps_api.delete_namespaced_deployment(
                name=name,
                namespace=self._settings.namespace,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
            self._core_api.delete_namespaced_service(name=name, namespace=self._settings.namespace)

            logger.info("Deleted instance {}.", instance_num)
        except Exception as error:
            logger.error("Failed to delete instance {}: {}", instance_num, error)
