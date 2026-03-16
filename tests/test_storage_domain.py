"""
Tests for storage/storage_domain: Folder, File.
"""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from chess_reporter.storage.storage_domain import File, Folder

# ---------------------------------------------------------------------------
# Folder
# ---------------------------------------------------------------------------


def test_folder_valid(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    A valid Folder is created with the correct path.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    folder: Folder = Folder(parent_folder_name="input", child_folder_name="game")

    assert folder.parent_folder_name == "input"
    assert folder.child_folder_name == "game"
    assert folder.path == tmp_path / "input" / "game"


def test_folder_normalizes_case(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Folder names are normalized to lowercase.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    folder: Folder = Folder(parent_folder_name="INPUT", child_folder_name="GAME")

    assert folder.parent_folder_name == "input"
    assert folder.child_folder_name == "game"


def test_folder_invalid_parent_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    An invalid parent folder name raises a validation error.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    with raises(Exception):
        Folder(parent_folder_name="invalid", child_folder_name="game")


def test_folder_invalid_child_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    An invalid child folder name raises a validation error.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    with raises(Exception):
        Folder(parent_folder_name="input", child_folder_name="invalid")


def test_folder_exists_false_when_not_created(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    exists returns False when the folder does not exist on disk.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    folder: Folder = Folder(parent_folder_name="input", child_folder_name="game")

    assert folder.exists is False


def test_folder_exists_true_when_created(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    exists returns True after the folder is created.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    folder: Folder = Folder(parent_folder_name="input", child_folder_name="game")

    folder.path.mkdir(parents=True, exist_ok=True)

    assert folder.exists is True


# ---------------------------------------------------------------------------
# File
# ---------------------------------------------------------------------------


def _make_folder(tmp_path: Path, monkeypatch: MonkeyPatch) -> Folder:
    """
    Helper that creates a valid Folder with STORAGE_PATH set.
    """
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    return Folder(parent_folder_name="input", child_folder_name="game")


def test_file_valid_json(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    A File with a json extension is valid and recognized as a string file.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="data.json")

    assert file.file_extension == "json"
    assert file.is_string is True
    assert file.is_binary is False
    assert file.name == "data"


def test_file_valid_pgn(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    A File with a pgn extension is valid and recognized as a binary file.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="game.pgn")

    assert file.file_extension == "pgn"
    assert file.is_binary is True
    assert file.is_string is False


def test_file_valid_xlsx(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    A File with an xlsx extension is recognized as binary.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="report.xlsx")

    assert file.is_binary is True


def test_file_valid_parquet(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    A File with a parquet extension is recognized as binary.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="data.parquet")

    assert file.is_binary is True


def test_file_invalid_extension_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    An unsupported file extension raises a validation error.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)

    with raises(Exception):
        File(folder=folder, file_name="data.csv")


def test_file_empty_name_raises(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    An empty file name raises a validation error.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)

    with raises(Exception):
        File(folder=folder, file_name="")


def test_file_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    File path is correctly constructed from folder + file_name.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="game.pgn")

    assert file.path == folder.path / "game.pgn"


def test_file_exists_false_when_not_on_disk(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    exists returns False when the file is not on disk.
    """
    folder: Folder = _make_folder(tmp_path, monkeypatch)
    file: File = File(folder=folder, file_name="game.pgn")

    assert file.exists is False
