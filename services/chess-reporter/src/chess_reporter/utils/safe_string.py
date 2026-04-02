"""
Utils package: safe string module
"""

from __future__ import annotations

from json import dumps
from typing import Any


def safe_string(value: Any) -> str:
    """
    Convert a value to a safe string representation by removing newlines, carriage returns,
    and single quotes.

    Args:
        value (Any):
            The value to be converted to a safe string. This can be of any type, and it will
            be serialized to a JSON string if it's not already a string.

    Returns:
        A safe string representation of the input value.
    """
    if value is None:
        return ""

    safe_value: str = ""

    if not isinstance(value, str):
        try:
            safe_value = dumps(value, default=str, ensure_ascii=True, separators=(",", ":"))
        except Exception:
            safe_value = repr(value)
    else:
        safe_value = value

    safe_value = (
        safe_value.strip()
        .encode("utf-8", "replace")
        .decode("utf-8")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

    return safe_value
