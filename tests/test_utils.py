"""
Tests for utils: generate_hash_id, find_engine.
"""

from __future__ import annotations

from typing import Any

from chess_reporter.utils.find_engine import find_engine
from chess_reporter.utils.generate_hash_id import generate_hash_id

# ---------------------------------------------------------------------------
# generate_hash_id
# ---------------------------------------------------------------------------


def test_generate_hash_id_is_deterministic() -> None:
    """
    The same input always produces the same hash.
    """
    values: list[Any] = ["a", "b", 1]

    assert generate_hash_id(values) == generate_hash_id(values)


def test_generate_hash_id_different_inputs_differ() -> None:
    """
    Different values produce different hashes.
    """
    assert generate_hash_id(["a"]) != generate_hash_id(["b"])


def test_generate_hash_id_order_matters() -> None:
    """
    Input order is significant — [a, b] != [b, a].
    """
    assert generate_hash_id(["a", "b"]) != generate_hash_id(["b", "a"])


def test_generate_hash_id_returns_hex_string() -> None:
    """
    The result is a valid hex string.
    """
    result: str = generate_hash_id(["test"])

    assert isinstance(result, str)
    int(result, 16)  # raises if not valid hex


def test_generate_hash_id_sha512_length() -> None:
    """
    SHA-512 produces exactly 128 hex characters.
    """
    assert len(generate_hash_id(["test"])) == 128


def test_generate_hash_id_mixed_types() -> None:
    """
    Mixed-type lists are handled correctly.
    """
    result: str = generate_hash_id([1, "two", 3.0, None])

    assert isinstance(result, str)
    assert len(result) == 128


def test_generate_hash_id_empty_list() -> None:
    """
    An empty list produces a valid, deterministic hash.
    """
    result: str = generate_hash_id([])

    assert len(result) == 128
    assert generate_hash_id([]) == result


# ---------------------------------------------------------------------------
# find_engine
# ---------------------------------------------------------------------------


def test_find_engine_returns_non_empty_string() -> None:
    """
    find_engine always returns a non-empty string path (binary may or may not exist).
    """
    result: str = find_engine()

    assert isinstance(result, str)
    assert len(result) > 0
