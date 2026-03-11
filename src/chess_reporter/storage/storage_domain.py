"""
Storage configuration parameters for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from chess_reporter.storage.storage_parameters import StorageParameters


class Folder(BaseModel):
    """
    Represents a folder within the storage system, including its parent and child folder names.
    """

    parent_folder_name: str = Field(description="Name of the parent folder")
    child_folder_name: str = Field(description="Name of the child folder")

    def _validate_parent_folder_name(self) -> None:
        """
        Validates the parent folder name and adjusts it to be lowercase and stripped of whitespace.
        """

        self.parent_folder_name = self.parent_folder_name.lower().strip()

        if self.parent_folder_name not in StorageParameters().parent_folder_names:
            raise ValueError(
                f"Invalid folder name: '{self.parent_folder_name}'. "
                f"Valid options are: {StorageParameters().parent_folder_names}"
            )

    def _validate_child_folder_name(self) -> None:
        """
        Validates the child folder name and adjusts it to be lowercase and stripped of whitespace.
        """
        self.child_folder_name = self.child_folder_name.lower().strip()

        if self.child_folder_name not in StorageParameters().child_folder_names:
            raise ValueError(
                f"Invalid child folder name: '{self.child_folder_name}'. "
                f"Valid options are: {StorageParameters().child_folder_names}"
            )

    @model_validator(mode="after")
    def validate_folder_consistency(self) -> Folder:
        """
        Validates the consistency of the folder.
        """
        self._validate_parent_folder_name()
        self._validate_child_folder_name()

        return self

    @property
    def path(self) -> Path:
        """
        Path to the file within the storage directory
        """
        return StorageParameters().path / self.parent_folder_name / self.child_folder_name

    @property
    def exists(self) -> bool:
        """
        Flag indicating whether the folder exists at the specified path
        """
        return self.path.exists() and self.path.is_dir()


class File(BaseModel):
    """
    Represents a file within the storage system, including its folder and name.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    folder: Folder = Field(description="Folder where the file is located")
    file_name: str = Field(description="Name of the file, including extension")

    @property
    def name(self) -> str:
        """
        Name of the file without extension
        """
        try:
            return ".".join(self.file_name.split(".")[:-1])
        except Exception:
            return self.file_name

    @property
    def file_extension(self) -> str:
        """
        File extension of the file
        """
        try:
            return self.file_name.split(".")[-1].lower().strip()
        except Exception:
            return ""

    def _validate_file(self) -> None:
        """
        Validates the file name and extension.
        """
        self.file_name = self.file_name.strip()

        if len(self.file_name) == 0:
            raise ValueError("File name cannot be empty.")

        if self.file_extension not in StorageParameters().all_extensions:
            raise ValueError(
                f"Invalid file extension: '{self.file_extension}'. "
                f"Valid options are: {StorageParameters().all_extensions}"
            )

    @model_validator(mode="after")
    def validate_file_consistency(self) -> File:
        """
        Validates the consistency of the file.
        """
        self._validate_file()

        return self

    @property
    def path(self) -> Path:
        """
        Path to the file within the storage directory
        """
        return self.folder.path / self.file_name

    @property
    def exists(self) -> bool:
        """
        Flag indicating whether the file exists at the specified path
        """
        return self.path.exists() and self.path.is_file()

    @property
    def is_binary(self) -> bool:
        """
        Flag indicating whether the file is a binary file based on its extension
        """
        return self.file_extension in StorageParameters().binary_extensions

    @property
    def is_string(self) -> bool:
        """
        Flag indicating whether the file is a string file based on its extension
        """
        return self.file_extension in StorageParameters().string_extensions
