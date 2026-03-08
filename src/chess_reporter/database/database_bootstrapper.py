"""
Database bootstrapper for the Chess Reporter application.
"""

from __future__ import annotations

from pathlib import Path

from loguru import Logger, logger

from chess_reporter.database.database_manager import DatabaseManager


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
        sqls_dir: Path = Path(__file__).resolve().parent / "sqls"

        self.__schemas_file_path: Path = sqls_dir / "schemas.sql"
        self.__tables_file_path: Path = sqls_dir / "tables.sql"
        self.__logger: Logger = logger.bind(name="chess-reporter")

        self.__validate_sql_files()

    def __validate_sql_files(self) -> None:
        """
        Validates the existence of the SQL files for schemas and tables.
        """
        if not self.__schemas_file_path.exists():
            error: str = "Schemas SQL file not found at path: {}".format(self.__schemas_file_path)

            self.__logger.exception(error)
            raise FileNotFoundError(error)

        if not self.__tables_file_path.exists():
            error: str = "Tables SQL file not found at path: {}".format(self.__tables_file_path)

            self.__logger.exception(error)
            raise FileNotFoundError(error)

    def bootstrap(self) -> None:
        """
        Bootstraps the database by executing the SQL files for schemas and tables.
        """
        schemas_sqls: str = self.__schemas_file_path.read_text(encoding="utf-8")
        tables_sqls: str = self.__tables_file_path.read_text(encoding="utf-8")

        database_manager: DatabaseManager = DatabaseManager()

        try:
            database_manager.execute(schemas_sqls)
            database_manager.execute(tables_sqls)
        finally:
            database_manager.close()
