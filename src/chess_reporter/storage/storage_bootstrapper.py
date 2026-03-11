"""
Storage bootstrapper for the Chess Reporter application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from chess_reporter.storage.storage_domain import Folder
from chess_reporter.storage.storage_parameters import StorageParameters

if TYPE_CHECKING:
    from loguru import Logger


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
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: StorageParameters = StorageParameters()

    def bootstrap(self) -> None:
        """
        Bootstraps the storage by creating the necessary folder structure based on
        the provided storage parameters. It iterates through the specified folders
        and subfolders, checks if they exist, and creates them if they do not exist,
        while logging the actions taken.
        """
        for parent_folder_name in self._parameters.parent_folder_names:
            for child_folder_name in self._parameters.child_folder_names:
                folder: Folder = Folder(
                    parent_folder_name=parent_folder_name,
                    child_folder_name=child_folder_name,
                )

                if folder.exists:
                    self._logger.info("Storage folder already exists at path: {}", folder.path)
                else:
                    folder.path.mkdir(parents=True, exist_ok=True)
                    self._logger.info("Created storage folder at path: {}", folder.path)
