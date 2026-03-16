"""
Tests for database/database_manager: DatabaseManager.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pandas import DataFrame
from pytest import fixture, raises

from chess_reporter.database.database_domain import Query, QueryType
from chess_reporter.database.database_manager import DatabaseManager


@fixture
def manager(db_path: Path) -> DatabaseManager:
    """
    A DatabaseManager pointed at a fresh temp DB (non-bootstrapped, non-internal).
    """
    return DatabaseManager(internal=False)


@fixture
def internal_manager(db: Path) -> DatabaseManager:
    """
    An internal DatabaseManager pointed at a fully bootstrapped DB.
    """
    return DatabaseManager(internal=True)


# ---------------------------------------------------------------------------
# execute / query
# ---------------------------------------------------------------------------


def test_execute_ddl_creates_table(manager: DatabaseManager) -> None:
    """
    Executing a CREATE TABLE statement succeeds.
    """
    queries: list[Query] = manager.execute(
        "CREATE SCHEMA IF NOT EXISTS ws; "
        "CREATE TABLE IF NOT EXISTS ws.test (id TEXT PRIMARY KEY, val INTEGER);"
    )

    assert len(queries) == 2
    assert all(q.query_type == QueryType.DDL for q in queries)


def test_execute_dql_returns_dataframe(manager: DatabaseManager) -> None:
    """
    A SELECT statement returns a Query with a usable DataFrame.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws; CREATE TABLE ws.nums (n INTEGER);")
    manager.execute("INSERT INTO ws.nums VALUES (1), (2), (3);")

    queries: list[Query] = manager.execute("SELECT n FROM ws.nums ORDER BY n;")

    assert len(queries) == 1
    q: Query = queries[0]
    assert q.query_type == QueryType.DQL
    assert list(q.dataframe["n"]) == [1, 2, 3]


def test_query_single_statement(manager: DatabaseManager) -> None:
    """
    .query() executes exactly one statement and returns a single Query.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws; CREATE TABLE ws.x (v INTEGER);")
    manager.execute("INSERT INTO ws.x VALUES (42);")

    q: Query = manager.query("SELECT v FROM ws.x;")

    assert q.value == 42


def test_query_multiple_statements_raises(manager: DatabaseManager) -> None:
    """
    .query() raises when given more than one SQL statement.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws; CREATE TABLE ws.a (v INTEGER);")

    with raises(ValueError):
        manager.query("SELECT 1; SELECT 2;")


def test_execute_empty_sql_raises(manager: DatabaseManager) -> None:
    """
    Executing an empty string raises ValueError.
    """
    with raises(ValueError):
        manager.execute("")


# ---------------------------------------------------------------------------
# create_table
# ---------------------------------------------------------------------------


def test_create_table_from_dict(manager: DatabaseManager) -> None:
    """
    create_table accepts a single dict and creates a table.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws;")
    row: dict[str, Any] = {"id": "a1", "score": 10}

    manager.create_table(row, "ws.scores")

    q: Query = manager.query("SELECT COUNT(*) AS cnt FROM ws.scores;")
    assert q.value == 1


def test_create_table_from_list_of_dicts(manager: DatabaseManager) -> None:
    """
    create_table accepts a list of dicts.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws;")
    rows: list[dict[str, Any]] = [{"id": "a"}, {"id": "b"}]

    manager.create_table(rows, "ws.items")

    q: Query = manager.query("SELECT COUNT(*) AS cnt FROM ws.items;")
    assert q.value == 2


def test_create_table_from_dataframe(manager: DatabaseManager) -> None:
    """
    create_table accepts a DataFrame.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws;")
    df: DataFrame = DataFrame({"x": [1, 2, 3]})

    manager.create_table(df, "ws.nums")

    q: Query = manager.query("SELECT COUNT(*) AS cnt FROM ws.nums;")
    assert q.value == 3


def test_create_table_internal_raises(manager: DatabaseManager) -> None:
    """
    create_table on an internal (chess_reporter.*) table raises ValueError.
    """
    with raises(ValueError):
        manager.create_table({"id": "x"}, "chess_reporter.anything")


# ---------------------------------------------------------------------------
# insert
# ---------------------------------------------------------------------------


def test_insert_into_external_table(manager: DatabaseManager) -> None:
    """
    insert appends rows to an existing external table.
    """
    manager.execute("CREATE SCHEMA IF NOT EXISTS ws; CREATE TABLE ws.vals (id TEXT);")

    manager.insert({"id": "row1"}, "ws.vals")
    manager.insert({"id": "row2"}, "ws.vals")

    q: Query = manager.query("SELECT COUNT(*) AS cnt FROM ws.vals;")
    assert q.value == 2


def test_insert_internal_table_raises(manager: DatabaseManager) -> None:
    """
    insert on an internal table raises ValueError.
    """
    with raises(ValueError):
        manager.insert({"id": "x"}, "chess_reporter.status")


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------


def test_merge_internal_table_requires_internal_flag(db: Path) -> None:
    """
    merge on an internal table with internal=False raises ValueError.
    """
    non_internal: DatabaseManager = DatabaseManager(internal=False)

    with raises(ValueError):
        non_internal.merge({"id": "pending"}, "chess_reporter.status")


def test_merge_external_table_raises(db: Path) -> None:
    """
    merge on an external (non-internal) table raises ValueError even with internal=True.
    """
    mgr: DatabaseManager = DatabaseManager(internal=True)
    mgr.execute("CREATE SCHEMA IF NOT EXISTS ws; CREATE TABLE ws.t (id TEXT);")

    with raises(ValueError):
        mgr.merge({"id": "x"}, "ws.t")


# ---------------------------------------------------------------------------
# context manager
# ---------------------------------------------------------------------------


def test_database_manager_context_manager(db_path: Path) -> None:
    """
    DatabaseManager works correctly as a context manager.
    """
    with DatabaseManager() as mgr:
        queries: list[Query] = mgr.execute("SELECT 1 AS n;")

        assert len(queries) == 1
        assert queries[0].value == 1
