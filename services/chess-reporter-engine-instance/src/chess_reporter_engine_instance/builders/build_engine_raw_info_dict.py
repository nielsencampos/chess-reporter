"""
Engine instance: Build engine raw info dict module
"""

from __future__ import annotations

from typing import Any


def build_engine_raw_info_dict(value: Any) -> Any:
    """
    Recursively build a raw info dictionary from the given value, converting all keys to strings.

    Args:
        value (Any):
            The value to convert into a raw info dictionary.
            This can be of any type, including nested dictionaries, lists, and tuples.

    Returns:
        Any:
            The raw info dictionary with all keys converted to strings.
            If the input value is a dictionary, it will be processed recursively.
            If it's a list or tuple, each item will be processed recursively.
            For other types, the value will be returned as-is,
            except for non-primitive types which will be converted to their string representation.
    """
    if value is None:
        return None

    if isinstance(value, dict):
        new_dict: dict[str, Any] = {}

        for new_key, new_value in value.items():
            new_dict[str(new_key)] = build_engine_raw_info_dict(new_value)

        return new_dict

    if isinstance(value, list):
        return [build_engine_raw_info_dict(item) for item in value]

    if isinstance(value, tuple):
        return tuple(build_engine_raw_info_dict(item) for item in value)

    if not isinstance(value, (str, int, float, bool)):
        return str(value)

    return value
