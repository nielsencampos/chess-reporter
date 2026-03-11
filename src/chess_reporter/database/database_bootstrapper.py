"""
Database bootstrapper for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from chess_reporter.database.database_manager import DatabaseManager

if TYPE_CHECKING:
    from loguru import Logger


class DatabaseBootstrapper:
    """
    Bootstraps the database for the Chess Reporter application.

    Methods:
        bootstrap: Bootstraps the database by executing the SQL files for schemas and tables.
    """

    def __init__(self) -> None:
        """
        Initializes the DatabaseBootstrapper.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")

        sqls_dir: Path = Path(__file__).resolve().parent / "sqls"

        self._schemas_file_path: Path = sqls_dir / "schemas.sql"
        self._tables_file_path: Path = sqls_dir / "tables.sql"
        self._tests_file_path: Path = sqls_dir / "tests.sql"

        self._validate_sql_files()

    def _validate_sql_files(self) -> None:
        """
        Validates the existence of the SQL files for schemas and tables.
        """
        if not self._schemas_file_path.exists():
            error: str = "Schemas SQL file not found at path: {}".format(self._schemas_file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        if not self._tables_file_path.exists():
            error: str = "Tables SQL file not found at path: {}".format(self._tables_file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

        if not self._tests_file_path.exists():
            error: str = "Tests SQL file not found at path: {}".format(self._tests_file_path)

            self._logger.error(error)

            raise FileNotFoundError(error)

    def bootstrap(self) -> None:
        """
        Bootstraps the database by executing the SQL files for schemas and tables.
        """
        schemas_sqls: str = self._schemas_file_path.read_text(encoding="utf-8")
        tables_sqls: str = self._tables_file_path.read_text(encoding="utf-8")
        tests_sqls: str = self._tests_file_path.read_text(encoding="utf-8")

        with DatabaseManager() as database_manager:
            database_manager.execute(schemas_sqls)
            database_manager.execute(tables_sqls)
            database_manager.execute(tests_sqls)
