"""
Tests for storage/storage_manager: StorageManager.
"""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from chess_reporter.storage.storage_domain import File, Folder
from chess_reporter.storage.storage_manager import StorageManager


def _setup(tmp_path: Path, monkeypatch: MonkeyPatch) -> tuple[StorageManager, Folder]:
    """
    Sets up a StorageManager and a valid Folder with STORAGE_PATH monkeypatched.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    manager: StorageManager = StorageManager()
    folder: Folder = Folder(parent_folder_name="input", child_folder_name="game")
    folder.path.mkdir(parents=True, exist_ok=True)

    return manager, folder


# ---------------------------------------------------------------------------
# save_file / read_file — binary (pgn)
# ---------------------------------------------------------------------------


def test_save_and_read_binary_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Saving and reading a binary file (pgn) round-trips correctly.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="game.pgn")
    content: bytes = b'[Event "Test"]\n1. e4 e5 *'

    manager.save_file(content, file)

    result: bytes | str = manager.read_file(file)
    assert result == content


def test_save_and_read_text_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Saving and reading a text file (json) round-trips correctly.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="meta.json")
    content: str = '{"key": "value"}'

    manager.save_file(content, file)

    result: bytes | str = manager.read_file(file)
    assert result == content


def test_save_binary_with_string_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Saving a string to a binary file raises ValueError.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="game.pgn")

    with raises(ValueError):
        manager.save_file("not bytes", file)


def test_save_text_with_bytes_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Saving bytes to a text file raises ValueError.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="meta.json")

    with raises(ValueError):
        manager.save_file(b"bytes content", file)


# ---------------------------------------------------------------------------
# read_file errors
# ---------------------------------------------------------------------------


def test_read_file_not_found_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Reading a file that does not exist raises FileNotFoundError.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="missing.json")

    with raises(FileNotFoundError):
        manager.read_file(file)


# ---------------------------------------------------------------------------
# delete_file
# ---------------------------------------------------------------------------


def test_delete_existing_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Deleting an existing file removes it from disk.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="data.json")

    manager.save_file('{"x": 1}', file)
    assert file.exists is True

    manager.delete_file(file)
    assert file.exists is False


def test_delete_non_existent_file_is_noop(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Deleting a file that does not exist does not raise an error.
    """
    manager, folder = _setup(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="ghost.json")

    manager.delete_file(file)
