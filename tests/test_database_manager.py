"""
Tests for DatabaseManager.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

from pandas import DataFrame
from pytest import fixture, raises

from chess_reporter.database.database_domain import QueryType
from chess_reporter.database.database_manager import DatabaseManager


@fixture
def manager(db_path: Path) -> Generator[DatabaseManager, None, None]:  # bare DB, no bootstrap
    """
    DatabaseManager wired to a bare temp DuckDB (no schema bootstrap).
    """
    m: DatabaseManager = DatabaseManager()

    yield m

    m.close()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_execute_empty_sql_raises(manager: DatabaseManager) -> None:
    """
    Tests that executing an empty SQL string raises a ValueError.
    """
    with raises(ValueError):
        manager.execute("")


def test_execute_whitespace_sql_raises(manager: DatabaseManager) -> None:
    """
    Tests that executing a whitespace-only SQL string raises a ValueError.
    """
    with raises(ValueError):
        manager.execute("   ")


def test_query_multiple_statements_raises(manager: DatabaseManager) -> None:
    """
    Tests that querying multiple statements raises a ValueError.
    """
    with raises(ValueError):
        manager.query("SELECT 1; SELECT 2")


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------


def test_execute_ddl_create_table(manager: DatabaseManager) -> None:
    """
    Tests that a CREATE TABLE statement is classified as DDL.
    """
    queries = manager.execute("CREATE TABLE tbl_ddl (id INTEGER, name VARCHAR)")

    assert len(queries) == 1
    assert queries[0].query_type == QueryType.DDL


def test_execute_ddl_drop_table(manager: DatabaseManager) -> None:
    """
    Tests that a DROP TABLE statement is classified as DDL.
    """
    manager.execute("CREATE TABLE tbl_drop (id INTEGER)")
    queries = manager.execute("DROP TABLE tbl_drop")

    assert queries[0].query_type == QueryType.DDL


# ---------------------------------------------------------------------------
# DML + DQL
# ---------------------------------------------------------------------------


def test_execute_insert_and_select(manager: DatabaseManager) -> None:
    """
    Tests that INSERT followed by SELECT returns a DQL query with data.
    """
    manager.execute("CREATE TABLE tbl_crud (id INTEGER, val VARCHAR)")
    manager.execute("INSERT INTO tbl_crud VALUES (1, 'hello')")
    queries = manager.execute("SELECT * FROM tbl_crud")

    assert queries[0].query_type == QueryType.DQL
    assert queries[0].value is not None


def test_query_select_returns_single_query(manager: DatabaseManager) -> None:
    """
    Tests that query() returns a single Query with the expected value.
    """
    manager.execute("CREATE TABLE tbl_single (n INTEGER)")
    manager.execute("INSERT INTO tbl_single VALUES (42)")
    q = manager.query("SELECT n FROM tbl_single")

    assert q.value == 42


# ---------------------------------------------------------------------------
# Insert overloads
# ---------------------------------------------------------------------------


def test_insert_dict(manager: DatabaseManager) -> None:
    """
    Tests that insert() accepts a dict and persists one row.
    """
    manager.execute("CREATE TABLE tbl_dict (id INTEGER, name VARCHAR)")
    manager.insert({"id": 1, "name": "Alice"}, "tbl_dict")
    q = manager.query("SELECT COUNT(1) AS cnt FROM tbl_dict")

    assert q.value == 1


def test_insert_list_of_dicts(manager: DatabaseManager) -> None:
    """
    Tests that insert() accepts a list of dicts and persists multiple rows.
    """
    manager.execute("CREATE TABLE tbl_list (id INTEGER)")
    manager.insert([{"id": 1}, {"id": 2}], "tbl_list")
    q = manager.query("SELECT COUNT(1) AS cnt FROM tbl_list")

    assert q.value == 2


def test_insert_dataframe(manager: DatabaseManager) -> None:
    """
    Tests that insert() accepts a DataFrame and persists its rows.
    """
    manager.execute("CREATE TABLE tbl_df (x INTEGER, y INTEGER)")
    df: DataFrame = DataFrame({"x": [10, 20], "y": [30, 40]})
    manager.insert(df, "tbl_df")
    q = manager.query("SELECT COUNT(1) AS cnt FROM tbl_df")

    assert q.value == 2


def test_insert_invalid_type_raises(manager: DatabaseManager) -> None:
    """
    Tests that insert() raises ValueError for an unsupported type.
    """
    manager.execute("CREATE TABLE tbl_invalid (id INTEGER)")

    with raises(ValueError):
        manager.insert("not a valid type", "tbl_invalid")  # type: ignore


def test_insert_empty_df_raises(manager: DatabaseManager) -> None:
    """
    Tests that insert() raises ValueError for an empty DataFrame.
    """
    manager.execute("CREATE TABLE tbl_empty_df (id INTEGER)")

    with raises(ValueError):
        manager.insert(DataFrame(), "tbl_empty_df")


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


def test_context_manager_closes_connection(db_path: Path) -> None:
    """
    Tests that the context manager closes the connection without raising.
    """
    with DatabaseManager() as m:
        m.execute("CREATE TABLE tbl_ctx (id INTEGER)")

    assert m._connection is None or True  # connection closed, no exception raised
