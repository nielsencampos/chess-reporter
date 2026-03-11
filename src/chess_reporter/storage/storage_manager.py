"""
Storage manager for the Chess Reporter application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from loguru import logger

from chess_reporter.storage.storage_domain import File
from chess_reporter.storage.storage_parameters import StorageParameters

if TYPE_CHECKING:
    from loguru import Logger


class StorageManager:
    """
    Manages the storage operations for the Chess Reporter application.
    """

    def __init__(self) -> None:
        """
        Initializes the StorageManager.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: StorageParameters = StorageParameters()

    def read_file(self, file: File) -> Union[bytes, str]:
        """
        Reads the content of the specified file, returning it as bytes for
        binary files or as a string for text files.

        Args:
            file (File): The File object representing the file to read.

        Returns:
            Union[bytes, str]: The content of the file, returned as bytes for
                binary files or as a string for text files.
        """
        if not file.exists:
            error: str = "File not found at path: {}.".format(file.path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        if file.is_binary:
            return file.path.read_bytes()
        else:
            return file.path.read_text(encoding="utf-8")

    def save_file(self, content: Union[bytes, str], file: File) -> None:
        """
        Saves the provided content to the specified file, handling both binary and text files.

        Args:
            content (Union[bytes, str]): The content to save. Must be bytes for binary files and
                a string for text files.
            file (File): The File object representing the file to save to.
        """
        if file.is_binary:
            if not isinstance(content, bytes):
                error: str = "Content must be bytes for binary files."

                self._logger.error(error)

                raise ValueError(error)

            file.path.write_bytes(content)
        else:
            if not isinstance(content, str):
                error: str = "Content must be a string for text files."

                self._logger.error(error)

                raise ValueError(error)

            file.path.write_text(content, encoding="utf-8")

    def delete_file(self, file: File) -> None:
        """
        Deletes the specified file from the storage system.

        Args:
            file (File): The File object representing the file to delete.
        """
        if not file.exists:
            return

        file.path.unlink()
