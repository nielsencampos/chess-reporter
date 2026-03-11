"""
Tests for database_domain module.
"""

from __future__ import annotations

from pandas import DataFrame
from pytest import raises
from sqlglot import parse

from chess_reporter.database.database_domain import Query, QueryType


def _make_query(sql: str, data: DataFrame | None = None) -> Query:
    expression = parse(sql, dialect="duckdb")[0]

    assert expression is not None

    return Query(query_type=QueryType.DQL, expression=expression, data_returned=data)


# ---------------------------------------------------------------------------
# Query.sql
# ---------------------------------------------------------------------------


def test_query_sql_roundtrip() -> None:
    """
    Tests that the SQL string round-trips through the Query object correctly.
    """
    sql: str = "SELECT 1 AS value"
    q: Query = _make_query(sql)

    assert "SELECT" in q.sql.upper()
    assert "1" in q.sql


# ---------------------------------------------------------------------------
# Query.data / raw_data / row / value — with data
# ---------------------------------------------------------------------------


def test_query_data_returns_copy() -> None:
    """
    Tests that Query.data returns a DataFrame with the expected columns.
    """
    df: DataFrame = DataFrame({"a": [1, 2], "b": [3, 4]})
    q: Query = _make_query("SELECT 1", data=df)

    assert list(q.data.columns) == ["a", "b"]


def test_query_raw_data_is_list_of_dicts() -> None:
    """
    Tests that Query.raw_data returns a list of dictionaries.
    """
    df: DataFrame = DataFrame({"x": [10]})
    q: Query = _make_query("SELECT 1", data=df)

    assert q.raw_data == [{"x": 10}]


def test_query_row_returns_first_row() -> None:
    """
    Tests that Query.row returns the first row as a dictionary.
    """
    df: DataFrame = DataFrame({"v": [42, 99]})
    q: Query = _make_query("SELECT 1", data=df)

    assert q.row == {"v": 42}


def test_query_value_returns_first_cell() -> None:
    """
    Tests that Query.value returns the first cell of the first row.
    """
    df: DataFrame = DataFrame({"count": [7]})
    q: Query = _make_query("SELECT 1", data=df)

    assert q.value == 7


def test_query_columns_returns_column_list() -> None:
    """
    Tests that Query.columns returns the list of column names.
    """
    df: DataFrame = DataFrame({"a": [1], "b": [2]})
    q: Query = _make_query("SELECT 1", data=df)

    assert q.columns == ["a", "b"]


# ---------------------------------------------------------------------------
# Query.data raises when data_returned is None
# ---------------------------------------------------------------------------


def test_query_data_raises_when_none() -> None:
    """
    Tests that accessing Query.data raises ValueError when data_returned is None.
    """
    q: Query = _make_query("SELECT 1", data=None)

    with raises(ValueError):
        _ = q.data


def test_query_row_raises_when_no_data() -> None:
    """
    Tests that accessing Query.row raises ValueError when data_returned is None.
    """
    q: Query = _make_query("SELECT 1", data=None)

    with raises(ValueError):
        _ = q.row


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_query_model_dump_serializes_expression_as_string() -> None:
    """
    Tests that model_dump serializes the SQL expression as a string.
    """
    q: Query = _make_query("SELECT 1 AS v")
    dumped: dict = q.model_dump()

    assert isinstance(dumped["expression"], str)


def test_query_model_dump_serializes_none_data_as_none() -> None:
    """
    Tests that model_dump serializes None data_returned as None.
    """
    q: Query = _make_query("SELECT 1")
    dumped: dict = q.model_dump()

    assert dumped["data_returned"] is None
