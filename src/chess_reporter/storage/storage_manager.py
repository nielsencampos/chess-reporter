"""
Storage package: manager module
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from .storage_domain import File
from .storage_parameters import StorageParameters

if TYPE_CHECKING:
    from loguru import Logger


class StorageManager:
    """
    Storage Manager
    """

    def __init__(self) -> None:
        """
        Initializes the StorageManager.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: StorageParameters = StorageParameters()

    def read_file(self, file: File) -> bytes | str:
        """
        Reads the content of the specified file, returning it as bytes for
        binary files or as a string for text files.

        Args:
            file (File): The File object representing the file to read.

        Returns:
            bytes | str: The content of the file, returned as bytes for
                binary files or as a string for text files.
        """
        self._logger.debug("Reading file: {}", file.path)

        if not file.exists:
            error: str = "File not found at path: {}.".format(file.path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        if file.is_binary:
            self._logger.debug("File {} is binary. Reading as bytes.", file.path)

            return file.path.read_bytes()

        if file.is_string:
            self._logger.debug("File {} is text. Reading as string.", file.path)

            return file.path.read_text(encoding="utf-8")

        error: str = "Unsupported file type for reading content."

        self._logger.error(error)

        raise ValueError(error)

    def save_file(self, content: bytes | str, file: File) -> None:
        """
        Saves the provided content to the specified file, handling both binary and text files.

        Args:
            content (bytes | str): The content to save. Must be bytes for binary files and
                a string for text files.
            file (File): The File object representing the file to save to.
        """
        self._logger.debug("Saving content to file: {}", file.path)
        if file.is_binary:
            if not isinstance(content, bytes):
                error: str = "Content must be bytes for binary files."

                self._logger.error(error)

                raise ValueError(error)

            file.path.write_bytes(content)
            self._logger.info("Content saved to binary file: {}", file.path)

            return

        if file.is_string:
            if not isinstance(content, str):
                error: str = "Content must be a string for text files."

                self._logger.error(error)

                raise ValueError(error)

            file.path.write_text(content, encoding="utf-8")
            self._logger.info("Content saved to text file: {}", file.path)

            return

        error: str = "Unsupported file type for saving content."

        self._logger.error(error)

        raise ValueError(error)

    def delete_file(self, file: File) -> None:
        """
        Deletes the specified file from the storage system.

        Args:
            file (File): The File object representing the file to delete.
        """
        self._logger.debug("Deleting file: {}", file.path)

        if not file.exists:
            self._logger.warning("File not found for deletion: {}", file.path)

            return

        file.path.unlink()

        self._logger.info("File deleted: {}", file.path)
