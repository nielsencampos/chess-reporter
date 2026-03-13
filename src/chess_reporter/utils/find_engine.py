"""
Utils: Find engine
"""

from __future__ import annotations

from pathlib import Path
from platform import system
from shutil import which


def find_engine() -> str:
    """
    Attempts to find the Stockfish binary in common locations.

    Returns:
        The path to the Stockfish binary if found, otherwise a default path.
    """
    if system() == "Windows":
        win_path: Path = Path(__file__).parent.parent.parent.parent / "bin" / "stockfish.exe"
        if win_path.exists():
            return str(win_path)

    found = which("stockfish")

    if found:
        return found

    linux_path: Path = Path("/usr/local/bin/stockfish")

    if linux_path.exists():
        return str(linux_path)

    return "/usr/local/bin/stockfish"
