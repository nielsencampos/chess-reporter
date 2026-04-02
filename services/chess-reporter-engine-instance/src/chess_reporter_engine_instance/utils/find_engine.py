"""
Engine instance: find engine module.
"""

from __future__ import annotations

from pathlib import Path
from platform import system
from shutil import which


def find_engine() -> str:
    """
    Resolves the engine binary path.

    Resolution order:
      1. Windows: bin/stockfish.exe relative to the project root
      2. PATH (via shutil.which)
      3. /usr/local/bin/stockfish (Linux/Docker default)

    Returns:
        str: The resolved path to the engine binary.
    """
    if system() == "Windows":
        win_path: Path = Path(__file__).parent.parent.parent.parent / "bin" / "stockfish.exe"

        if win_path.exists():
            return str(win_path)

    found: str | None = which("stockfish")

    if found:
        return found

    linux_path: Path = Path("/usr/local/bin/stockfish")

    if linux_path.exists():
        return str(linux_path)

    # Final fallback — expected location in Docker image
    return "/usr/local/bin/stockfish"
