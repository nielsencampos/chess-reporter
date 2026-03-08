"""
Storage bootstrapper for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from chess_reporter.storage.storage_parameters import StorageParameters


class StorageBootstrapper:
    """
    Bootstraps the storage for the Chess Reporter application.

    Methods:
        bootstrap: Bootstraps the database by executing the SQL files for schemas and tables.
    """

    def __init__(self) -> None:
        """
        Initializes the StorageBootstrapper.
        """
        self.__parameters: StorageParameters = StorageParameters()
        self.__logger = logger.bind(name="chess-reporter")

    def bootstrap(self) -> None:
        """
        Bootstraps the storage by creating the necessary folders as defined in the parameters.
        """
        for folder_name in self.__parameters.folders:
            folder_path: Path = self.__parameters.path / folder_name

            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                self.__logger.info("Created storage folder at path: {}", folder_path)
            else:
                self.__logger.info("Storage folder already exists at path: {}", folder_path)
