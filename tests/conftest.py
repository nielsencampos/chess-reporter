"""
Shared test fixtures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

from pytest import MonkeyPatch, fixture

from chess_reporter.database.database_bootstrapper import DatabaseBootstrapper


@fixture
def db_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """
    Bare temp DuckDB path — no schema bootstrap. For raw DatabaseManager tests.

    Args:
        tmp_path: pytest fixture for temporary directory.
        monkeypatch: pytest fixture for patching environment variables.

    Yields:
        Path to the temporary DuckDB file.
    """
    path: Path = tmp_path / "raw.duckdb"

    monkeypatch.setenv("DATABASE_PATH", str(path))

    yield path


@fixture
def db(tmp_path: Path, monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """
    Fully bootstrapped temp DuckDB (chess_reporter schema). For pipeline tests.

    Args:
        tmp_path: pytest fixture for temporary directory.
        monkeypatch: pytest fixture for patching environment variables.

    Yields:
        Path to the temporary DuckDB file.
    """
    db_path: Path = tmp_path / "app.duckdb"

    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    DatabaseBootstrapper().bootstrap()

    yield db_path
