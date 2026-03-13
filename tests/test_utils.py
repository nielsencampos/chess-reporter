"""
Tests for utils module.
"""

from __future__ import annotations

from chess_reporter.utils.generate_hash_id import generate_hash_id


def test_generate_hash_id_is_deterministic() -> None:
    assert generate_hash_id(["a", "b", 1]) == generate_hash_id(["a", "b", 1])


def test_generate_hash_id_different_inputs_differ() -> None:
    assert generate_hash_id(["a"]) != generate_hash_id(["b"])


def test_generate_hash_id_order_matters() -> None:
    assert generate_hash_id(["a", "b"]) != generate_hash_id(["b", "a"])


def test_generate_hash_id_returns_hex_string() -> None:
    result = generate_hash_id(["test"])
    assert isinstance(result, str)
    int(result, 16)  # raises if not valid hex


def test_generate_hash_id_sha512_length() -> None:
    # SHA-512 produces 128 hex characters
    assert len(generate_hash_id(["test"])) == 128


def test_generate_hash_id_mixed_types() -> None:
    result = generate_hash_id([1, "two", 3.0, None])
    assert isinstance(result, str)
    assert len(result) == 128
