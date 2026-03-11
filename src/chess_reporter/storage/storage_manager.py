"""
Storage manager for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union

from loguru import logger

from chess_reporter.storage.storage_parameters import StorageParameters

if TYPE_CHECKING:
    from loguru import Logger


class StorageManager:
    """
    Manages the file system storage.

    Methods:
        list_files: Lists the files in a specified folder, optionally filtering by file extension.
        file_path: Returns the full path of a specified file in a given folder.
        file_exists: Checks if a specified file exists in a given folder.
        delete_file: Deletes a specified file from a given folder.
        read_file: Reads the content of a specified file from a given folder, returning it as
            either a string or bytes depending on the file type.
        save_file: Saves the given content to a specified file in a given folder, handling both
            string and binary content based on the file extension.
    """

    def __init__(self) -> None:
        """
        Initializes the StorageManager.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: StorageParameters = StorageParameters()

    def _get_folder_path(self, folder_name: str, subfolder_name: str) -> Path:
        """
        Checks if the provided folder name and subfolder name are valid according to the storage
            parameters.

        Args:
            folder_name (str): The name of the folder to check.
            subfolder_name (str): The name of the subfolder to check.
        """
        if folder_name not in self._parameters.folders:
            error: str = "Invalid folder name: {}. Valid folders are: {}.".format(
                folder_name, self._parameters.folders
            )

            self._logger.error(error)

            raise ValueError(error)

        if subfolder_name not in self._parameters.subfolders:
            error: str = "Invalid subfolder name: {}. Valid subfolders are: {}.".format(
                subfolder_name, self._parameters.subfolders
            )

            self._logger.error(error)

            raise ValueError(error)

        folder_path: Path = self._parameters.path / folder_name / subfolder_name

        return folder_path

    def _check_file_extension(self, file_extension: str) -> None:
        """
        Checks if the provided file extension is valid according to the storage parameters.

        Args:
            file_extension (str): The file extension to check,
                excluding the leading dot (e.g., "txt").
        """
        if file_extension not in self._parameters.all_extensions:
            error: str = "Invalid file extension: {}. Valid extensions are: {}.".format(
                file_extension,
                self._parameters.all_extensions,
            )

            self._logger.error(error)

            raise ValueError(error)

    def _get_file_path(self, folder_name: str, subfolder_name: str, file_name: str) -> Path:
        """
        Constructs the file path for the given folder name, subfolder name, and file name, and
        checks if the file has a valid extension.

        Args:
            folder_name (str): The name of the folder containing the file.
            subfolder_name (str): The name of the subfolder containing the file.
            file_name (str): The name of the file.

        Returns:
            Path: The constructed file path.
        """
        folder_path: Path = self._get_folder_path(folder_name, subfolder_name)
        file_path: Path = folder_path / file_name
        file_extension: str = file_path.suffix.replace(".", "").lower()

        self._check_file_extension(file_extension)

        return file_path

    def _read_file_as_string(self, file_path: Path) -> str:
        """
        Reads the content of the file at the provided path as a string.

        Args:
            file_path (Path): The path to the file to read.

        Returns:
            str: The content of the file as a string.
        """
        if not file_path.is_file():
            error: str = "File not found at path: {}.".format(file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension not in self._parameters.string_extensions:
            error: str = (
                "File at path: {} has an invalid extension: {}. Valid string extensions are: {}."
            ).format(
                file_path,
                file_extension,
                self._parameters.string_extensions,
            )

            self._logger.error(error)

            raise ValueError(error)

        return file_path.read_text(encoding="utf-8")

    def _read_file_as_binary(self, file_path: Path) -> bytes:
        """
        Reads the content of the file at the provided path as binary data.

        Args:
            file_path (Path): The path to the file to read.

        Returns:
            bytes: The content of the file as binary data.
        """
        if not file_path.is_file():
            error: str = "File not found at path: {}.".format(file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension not in self._parameters.binary_extensions:
            error: str = (
                "File at path: {} has an invalid extension: {}. Valid binary extensions are: {}."
            ).format(
                file_path,
                file_extension,
                self._parameters.binary_extensions,
            )

            self._logger.exception(error)

            raise ValueError(error)

        return file_path.read_bytes()

    def _save_file_as_string(self, content: str, file_path: Path) -> None:
        """
        Saves the provided string content to a file at the specified path.

        Args:
            content (str): The string content to save to the file.
            file_path (Path): The path where the file should be saved.
        """
        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension not in self._parameters.string_extensions:
            error: str = (
                "File at path: {} has an invalid extension: {}. Valid string extensions are: {}."
            ).format(
                file_path,
                file_extension,
                self._parameters.string_extensions,
            )

            self._logger.error(error)

            raise ValueError(error)

        file_path.write_text(content, encoding="utf-8")

    def _save_file_as_binary(self, content: bytes, file_path: Path) -> None:
        """
        Saves the provided binary content to a file at the specified path.

        Args:
            content (bytes): The binary content to save to the file.
            file_path (Path): The path where the file should be saved.
        """
        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension not in self._parameters.binary_extensions:
            error: str = (
                "File at path: {} has an invalid extension: {}. Valid binary extensions are: {}."
            ).format(
                file_path,
                file_extension,
                self._parameters.binary_extensions,
            )

            self._logger.error(error)

            raise ValueError(error)

        file_path.write_bytes(content)

    def list_files(
        self, folder_name: str, subfolder_name: str, file_extension: Optional[str] = None
    ) -> List[Path]:
        """
        Lists the files in the specified folder, optionally filtering by file extension.

        Args:
            folder_name (str): The name of the folder to list files from.
            subfolder_name (str): The name of the subfolder to list files from.
            file_extension (Optional[str]): The file extension to filter by (e.g., "txt").
                If None, all files will be listed regardless of extension.

        Returns:
            List[Path]: A list of Path objects representing the files in the specified folder
                that match the optional file extension filter.
        """
        folder_path: Path = self._get_folder_path(folder_name, subfolder_name)

        if file_extension is not None:
            self._check_file_extension(file_extension)

        if file_extension is not None and file_extension not in self._parameters.all_extensions:
            error: str = "Invalid file extension: {}. Valid extensions are: {}.".format(
                file_extension,
                self._parameters.all_extensions,
            )

            self._logger.error(error)

            raise ValueError(error)

        files: List[Path] = [file for file in folder_path.iterdir() if file.is_file()]

        if file_extension is not None:
            file_extension = file_extension.lower()
            files = [
                file for file in files if file.suffix.replace(".", "").lower() == file_extension
            ]
        else:
            valid_extensions = tuple(self._parameters.all_extensions)
            files = [
                file for file in files if file.suffix.replace(".", "").lower() in valid_extensions
            ]

        return files.copy()

    def file_exists(self, folder_name: str, subfolder_name: str, file_name: str) -> bool:
        """
        Checks if a file with the specified name exists in the given folder and subfolder.

        Args:
            folder_name (str): The name of the folder to check for the file.
            subfolder_name (str): The name of the subfolder to check for the file.
            file_name (str): The name of the file to check for.

        Returns:
            bool: True if the file exists in the specified folder and subfolder, False otherwise.
        """
        file_path: Path = self._get_file_path(folder_name, subfolder_name, file_name)

        return file_path.is_file()

    def file_path(self, folder_name: str, subfolder_name: str, file_name: str) -> Path:
        """
        Returns the full path of the specified file in the given folder and subfolder.

        Args:
            folder_name (str): The name of the folder containing the file.
            subfolder_name (str): The name of the subfolder containing the file.
            file_name (str): The name of the file.

        Returns:
            Path: The full path of the specified file.
        """
        return self._get_file_path(folder_name, subfolder_name, file_name)

    def delete_file(self, folder_name: str, subfolder_name: str, file_name: str) -> None:
        """
        Deletes the specified file from the given folder and subfolder.

        Args:
            folder_name (str): The name of the folder containing the file to delete.
            subfolder_name (str): The name of the subfolder containing the file to delete.
            file_name (str): The name of the file to delete.
        """
        file_path: Path = self._get_file_path(folder_name, subfolder_name, file_name)

        if not file_path.is_file():
            error: str = "File not found at path: {}.".format(file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        file_path.unlink()

    def read_file(self, folder_name: str, subfolder_name: str, file_name: str) -> Union[str, bytes]:
        file_path: Path = self._get_file_path(folder_name, subfolder_name, file_name)
        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension in self._parameters.string_extensions:
            return self._read_file_as_string(file_path)
        elif file_extension in self._parameters.binary_extensions:
            return self._read_file_as_binary(file_path)
        else:
            error: str = "File at path: {} has an invalid extension: {}.".format(
                file_path, file_extension
            )

            self._logger.error(error)

            raise ValueError(error)

    def save_file(
        self, content: Union[str, bytes], folder_name: str, subfolder_name: str, file_name: str
    ) -> None:
        """
        Saves the given content to a file in the specified folder and subfolder.

        Args:
            content (Union[str, bytes]): The content to save. Must be a string for text files and
                bytes for binary files.
            folder_name (str): The name of the folder to save the file in.
            subfolder_name (str): The name of the subfolder to save the file in.
            file_name (str): The name of the file to save.
        """
        file_path: Path = self._get_file_path(folder_name, subfolder_name, file_name)
        file_extension: str = file_path.suffix.replace(".", "").lower()

        if file_extension in self._parameters.string_extensions:
            if not isinstance(content, str):
                error: str = "Content must be a string for file extension: {}.".format(
                    file_extension
                )

                self._logger.error(error)

                raise ValueError(error)

            self._save_file_as_string(content, file_path)
        elif file_extension in self._parameters.binary_extensions:
            if not isinstance(content, bytes):
                error: str = "Content must be bytes for file extension: {}.".format(file_extension)

                self._logger.error(error)

                raise ValueError(error)

            self._save_file_as_binary(content, file_path)
        else:
            error: str = "File at path: {} has an invalid extension: {}.".format(
                file_path, file_extension
            )

            self._logger.error(error)

            raise ValueError(error)
