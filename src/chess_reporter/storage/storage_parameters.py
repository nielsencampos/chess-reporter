"""
Storage configuration parameters for the Chess Reporter application.
"""

from __future__ import annotations

from os import environ
from pathlib import Path
from typing import Set

from pydantic import BaseModel, Field


class StorageParameters(BaseModel):
    """
    Configuration parameters for the storage system.
    """

    path: Path = Field(
        default_factory=lambda: Path(environ.get("STORAGE_PATH", "data/storage")),
        description="Path to the storage directory",
    )
    folders: Set[str] = Field(
        default={"input", "output"},
        description="Set of folder names to be created within the storage directory",
    )
    subfolders: Set[str] = Field(
        default={"openings", "games", "others"},
        description="Set of subfolder names to be created within each folder",
    )
    binary_extensions: Set[str] = Field(
        default={"pgn", "xlsx"},
        description="Set of file extensions to be treated as binary files",
    )
    string_extensions: Set[str] = Field(
        default={"txt", "csv", "json", "jsonl"},
        description="Set of file extensions to be treated as string files",
    )

    @property
    def all_extensions(self) -> Set[str]:
        """
        Returns the set of all valid file extensions (both binary and string).
        """
        return self.binary_extensions.union(self.string_extensions)
