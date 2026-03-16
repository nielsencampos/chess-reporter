"""
Storage package: parameters module
"""

from __future__ import annotations

from os import environ
from pathlib import Path

from pydantic import BaseModel, Field


class StorageParameters(BaseModel):
    """
    Storage Parameters
    """

    path: Path = Field(
        default_factory=lambda: Path(environ.get("STORAGE_PATH", "data/storage")),
        description="Path to the storage directory",
        frozen=True,
    )
    parent_folder_names: set[str] = Field(
        default={"input", "output"},
        description="Set of parent folder names to be created within the storage directory",
        frozen=True,
    )
    child_folder_names: set[str] = Field(
        default={"opening", "game", "other"},
        description="Set of child folder names to be created within each parent folder",
        frozen=True,
    )
    binary_extensions: set[str] = Field(
        default={"parquet", "pgn", "xlsx"},
        description="Set of file extensions to be treated as binary files",
        frozen=True,
    )
    string_extensions: set[str] = Field(
        default={"json"},
        description="Set of file extensions to be treated as string files",
        frozen=True,
    )

    @property
    def all_extensions(self) -> set[str]:
        """
        Returns the set of all valid file extensions (both binary and string).
        """
        return self.binary_extensions.union(self.string_extensions)
