"""
Utils package: Generate hash ID module
"""

from __future__ import annotations

from hashlib import sha512
from json import dumps
from typing import Any


def generate_hash_id(values: list[Any]) -> str:
    """
    Generate a unique hash ID based on a list of values.

    Args:
        values (list[Any]): A list of values to generate the hash ID from.

    Returns:
        str: A unique hash ID generated from the input values.
    """
    concatenated_values: str = dumps(values, ensure_ascii=False, separators=(",", ":"), default=str)
    bytes_concatenated_values: bytes = concatenated_values.encode("utf-8")
    hash_value: str = sha512(bytes_concatenated_values).hexdigest()

    return hash_value
