"""
Database package: bootstrapper module
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from .database_manager import DatabaseManager

if TYPE_CHECKING:
    from loguru import Logger


class DatabaseBootstrapper:
    """
    Database Bootstrapper
    """

    def __init__(self) -> None:
        """
        Initializes the DatabaseBootstrapper.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")

        sql_path: Path = Path(__file__).resolve().parent / "sql"

        self._schema_path: Path = sql_path / "schema"
        self._table_path: Path = sql_path / "table"
        self._view_path: Path = sql_path / "view"

    def _list_sql_files(self, path: Path) -> list[Path]:
        """
        Lists all SQL files in the given directory.

        Args:
            path (Path): The directory path to list SQL files from.

        Returns:
            list[Path]: A list of SQL file paths.
        """
        if not path.exists() or not path.is_dir():
            return []

        return sorted(path.glob("*.sql"))

    def _read_sql_file(self, file_path: Path) -> str:
        """
        Reads the content of an SQL file.

        Args:
            file_path (Path): The path to the SQL file.

        Returns:
            str: The content of the SQL file.
        """
        with file_path.open("r", encoding="utf-8") as file:
            return file.read()

    def _execute_sql_files(self, database_manager: DatabaseManager, path: Path) -> None:
        """
        Executes all SQL files in the given directory using the provided DatabaseManager.

        Args:
            database_manager (DatabaseManager):
                The DatabaseManager instance to execute SQL commands.
            path (Path):
                The directory path to list SQL files from.
        """
        for sql_file in self._list_sql_files(path):
            try:
                sql: str = self._read_sql_file(sql_file)

                database_manager.execute(sql)
            except Exception:
                self._logger.error("Failed to execute SQL file {}", sql_file)

                raise

    def bootstrap(self) -> None:
        """
        Bootstraps the database by executing the SQL files for schemas, tables, and views.
        """
        with DatabaseManager() as database_manager:
            self._execute_sql_files(database_manager, self._schema_path)
            self._execute_sql_files(database_manager, self._table_path)
            self._execute_sql_files(database_manager, self._view_path)
