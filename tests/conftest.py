"""
Shared test fixtures.
"""

from __future__ import annotations

from pathlib import Path
from platform import system
from shutil import which
from typing import Generator, Optional

from pydantic import ConfigDict, Field
from pytest import MonkeyPatch, fixture, skip

from chess_reporter.chess_engine.chess_engine_parameters import ChessEngineParameters
from chess_reporter.database.database_bootstrapper import DatabaseBootstrapper


def _find_stockfish() -> Optional[str]:
    """
    Attempts to find the Stockfish binary in common locations.

    Returns:
        The path to the Stockfish binary if found, otherwise None.
    """
    if system() == "Windows":
        win_path: Path = Path(__file__).parent.parent / "bin" / "stockfish.exe"
        if win_path.exists():
            return str(win_path)

    found = which("stockfish")

    if found:
        return found

    linux_path: Path = Path("/usr/local/bin/stockfish")

    if linux_path.exists():
        return str(linux_path)

    return None


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


@fixture
def fast_engine_params(monkeypatch: MonkeyPatch) -> None:
    """
    Patches ChessEngineParameters to use minimum settings for speed.
    Skips the test if Stockfish is not found.

    Args:
        monkeypatch: pytest fixture for patching module attributes.
    """
    stockfish_path: Optional[str] = _find_stockfish()

    if stockfish_path is None:
        skip("Stockfish binary not found")

    class _FastParams(ChessEngineParameters):
        model_config = ConfigDict(frozen=True)
        path: str = Field(default=stockfish_path, frozen=True)
        threads: int = Field(default=1, frozen=True)
        hash_table_mb: int = Field(default=1024, frozen=True)
        depth: int = Field(default=15, frozen=True)
        evaluation_runs: int = Field(default=3, frozen=True)

    monkeypatch.setattr(
        "chess_reporter.chess_engine.chess_engine_instance.ChessEngineParameters",
        _FastParams,
    )
