"""
Utils package: find engine module
"""

from __future__ import annotations

from pathlib import Path
from platform import system
from shutil import which


def find_engine() -> str:
    """
    Attempt to find the chess engine binary on the system.

    Returns:
        The path to the chess engine binary if found, otherwise a default path.
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
