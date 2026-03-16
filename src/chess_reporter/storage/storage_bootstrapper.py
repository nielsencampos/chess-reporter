"""
Storage package: bootstrapper module
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from .storage_domain import Folder
from .storage_parameters import StorageParameters

if TYPE_CHECKING:
    from loguru import Logger


class StorageBootstrapper:
    """
    Storage Bootstrapper
    """

    def __init__(self) -> None:
        """
        Initializes the StorageBootstrapper.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: StorageParameters = StorageParameters()

    def bootstrap(self) -> None:
        """
        Bootstraps the storage by creating the necessary folders for the Chess Reporter application.
        """
        for parent_folder_name in self._parameters.parent_folder_names:
            for child_folder_name in self._parameters.child_folder_names:
                folder: Folder = Folder(
                    parent_folder_name=parent_folder_name,
                    child_folder_name=child_folder_name,
                )

                if folder.exists:
                    self._logger.info("Storage folder already exists at path: {}", folder.path)

                    continue

                folder.path.mkdir(parents=True, exist_ok=True)
                self._logger.info("Created storage folder at path: {}", folder.path)
