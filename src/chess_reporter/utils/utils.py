"""
Utility functions for the Chess Reporter application.
"""

from __future__ import annotations

from hashlib import sha512
from json import dumps
from shutil import which
from sys import platform
from typing import Any, List, Optional


def get_chess_engine_path() -> str:
    """
    Get the path to the chess engine executable.

    Returns:
        str: The path to the chess engine executable.
    """
    stockfish_found: Optional[str] = which("stockfish")

    if stockfish_found is not None:
        return stockfish_found

    if platform == "win32":
        return "bin/stockfish.exe"

    return "/usr/local/bin/stockfish"


def generate_hash_id(values: List[Any]) -> str:
    """
    Generate a unique hash ID based on a list of values.

    Args:
        values (List[Any]): A list of values to generate the hash ID from.

    Returns:
        str: A unique hash ID generated from the input values.
    """
    if not isinstance(values, list):
        raise TypeError("Values must be a list.")

    if len(values) == 0:
        raise ValueError("Values list cannot be empty.")

    if all(value is None for value in values):
        raise ValueError("Values list cannot contain only None values.")

    concatenated_values: str = dumps(values, ensure_ascii=False, separators=(",", ":"), default=str)
    bytes_concatenated_values: bytes = concatenated_values.encode("utf-8")
    hash_value: str = sha512(bytes_concatenated_values).hexdigest()

    return hash_value
