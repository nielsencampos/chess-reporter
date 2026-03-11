"""
Tests for StorageManager — binary (xlsx) and text (json) files.
"""

from __future__ import annotations

import json
from io import BytesIO

import pytest
from pandas import DataFrame

from chess_reporter.storage.storage_domain import File, Folder
from chess_reporter.storage.storage_manager import StorageManager


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    for parent in ("input", "output"):
        for child in ("openings", "games", "others"):
            (tmp_path / parent / child).mkdir(parents=True)
    return StorageManager()


def _file(file_name: str, parent: str = "output", child: str = "others") -> File:
    return File(
        folder=Folder(parent_folder_name=parent, child_folder_name=child),
        file_name=file_name,
    )


# ---------------------------------------------------------------------------
# Binary — xlsx (one row, chess_engine shape)
# ---------------------------------------------------------------------------


def test_save_and_read_xlsx(storage) -> None:
    df = DataFrame(
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

    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")

    f = _file("chess_engine.xlsx")
    storage.save_file(buf.getvalue(), f)

    result = storage.read_file(f)
    assert isinstance(result, bytes)
    assert result == buf.getvalue()


def test_save_xlsx_with_string_raises(storage) -> None:
    with pytest.raises(ValueError):
        storage.save_file("not bytes", _file("report.xlsx"))  # type: ignore


# ---------------------------------------------------------------------------
# Text — json
# ---------------------------------------------------------------------------


def test_save_and_read_json(storage) -> None:
    payload = json.dumps({"chess_engine_id": "abc123", "name": "Stockfish 18"})
    f = _file("chess_engine.json")
    storage.save_file(payload, f)
    assert storage.read_file(f) == payload


def test_save_json_with_bytes_raises(storage) -> None:
    with pytest.raises(ValueError):
        storage.save_file(b"bytes", _file("data.json"))  # type: ignore


def test_read_missing_file_raises(storage) -> None:
    with pytest.raises(FileNotFoundError):
        storage.read_file(_file("missing.json"))
