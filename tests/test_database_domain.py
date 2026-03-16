"""
Tests for database/database_domain: QueryType, Table.
"""

from __future__ import annotations

from pytest import raises

from chess_reporter.database.database_domain import QueryType, Table

# ---------------------------------------------------------------------------
# QueryType
# ---------------------------------------------------------------------------


def test_query_type_values() -> None:
    """
    All four query types have the correct string values.
    """
    assert QueryType.DQL == "dql"
    assert QueryType.DML == "dml"
    assert QueryType.DDL == "ddl"
    assert QueryType.DCL == "dcl"


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------


def test_table_valid_format() -> None:
    """
    A valid schema.table string produces a Table with correct parts.
    """
    table: Table = Table("workspace.games")

    assert str(table) == "workspace.games"
    assert table.schema_name == "workspace"
    assert table.table_name == "games"


def test_table_normalizes_to_lowercase() -> None:
    """
    Table normalizes the input to lowercase.
    """
    table: Table = Table("Workspace.Games")

    assert str(table) == "workspace.games"


def test_table_is_internal_true_for_chess_reporter_schema() -> None:
    """
    Tables under the chess_reporter schema are marked as internal.
    """
    table: Table = Table("chess_reporter.status")

    assert table.is_internal is True


def test_table_is_internal_false_for_other_schemas() -> None:
    """
    Tables under any other schema are not internal.
    """
    table: Table = Table("workspace.games")

    assert table.is_internal is False


def test_table_temp_name_format() -> None:
    """
    temp_name starts with _tmp_ and contains the table path.
    """
    table: Table = Table("workspace.games")
    temp: str = table.temp_name

    assert temp.startswith("_tmp_workspace_games_")
    assert len(temp) > len("_tmp_workspace_games_")


def test_table_temp_name_is_unique() -> None:
    """
    Successive calls to temp_name return different values.
    """
    table: Table = Table("workspace.games")

    assert table.temp_name != table.temp_name


def test_table_invalid_no_dot_raises() -> None:
    """
    A string without a dot raises a validation error.
    """
    with raises(Exception):
        Table("nodot")


def test_table_invalid_too_many_dots_raises() -> None:
    """
    A string with more than one dot raises a validation error.
    """
    with raises(Exception):
        Table("a.b.c")


def test_table_invalid_non_identifier_raises() -> None:
    """
    Non-identifier components raise a validation error.
    """
    with raises(Exception):
        Table("123schema.table")
