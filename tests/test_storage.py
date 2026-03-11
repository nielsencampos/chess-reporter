"""
Tests for StorageManager — binary (xlsx) and text (json) files.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from pandas import DataFrame
from pytest import MonkeyPatch, fixture, raises

from chess_reporter.storage.storage_domain import File, Folder
from chess_reporter.storage.storage_manager import StorageManager


@fixture
def storage(tmp_path: Path, monkeypatch: MonkeyPatch) -> StorageManager:
    """

    StorageManager wired to a fully structured temp directory.

    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    for parent in ("input", "output"):
        for child in ("openings", "games", "others"):
            (tmp_path / parent / child).mkdir(parents=True)

    return StorageManager()


def _file(file_name: str, parent: str = "output", child: str = "others") -> File:
    """

    Builds a File domain object pointing to the given path within the temp storage.

    """

    return File(
        folder=Folder(parent_folder_name=parent, child_folder_name=child),
        file_name=file_name,
    )


# ---------------------------------------------------------------------------
# Binary — xlsx (one row, chess_engine shape)
# ---------------------------------------------------------------------------


def test_save_and_read_xlsx(storage) -> None:
    """

    Saves an xlsx buffer and verifies the bytes round-trip correctly.

    """
    df: DataFrame = DataFrame(
        [
            {
                "chess_engine_id": "abc123",
                "name": "Stockfish 18",
                "threads": 4,
                "hash_table_mb": 4096,
                "depth": 30,
                "evaluation_runs": 5,
            }
        ]
    )
    buf: BytesIO = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")

    f: File = _file("chess_engine.xlsx")
    storage.save_file(buf.getvalue(), f)

    result: bytes = storage.read_file(f)

    assert isinstance(result, bytes)
    assert result == buf.getvalue()


def test_save_xlsx_with_string_raises(storage) -> None:
    """

    Passing a string to save_file for an xlsx file raises ValueError.

    """
    with raises(ValueError):
        storage.save_file("not bytes", _file("report.xlsx"))  # type: ignore


# ---------------------------------------------------------------------------
# Text — json
# ---------------------------------------------------------------------------


def test_save_and_read_json(storage) -> None:
    """

    Saves a JSON string and verifies the text round-trip correctly.

    """
    payload: str = json.dumps({"chess_engine_id": "abc123", "name": "Stockfish 18"})
    f: File = _file("chess_engine.json")
    storage.save_file(payload, f)

    assert storage.read_file(f) == payload


def test_save_json_with_bytes_raises(storage) -> None:
    """

    Passing bytes to save_file for a json file raises ValueError.

    """
    with raises(ValueError):
        storage.save_file(b"bytes", _file("data.json"))  # type: ignore


def test_read_missing_file_raises(storage) -> None:
    """

    Reading a non-existent file raises FileNotFoundError.

    """
    with raises(FileNotFoundError):
        storage.read_file(_file("missing.json"))
