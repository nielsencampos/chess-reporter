"""
Database package: manager module
"""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Any, ClassVar, overload

from duckdb import DuckDBPyConnection, connect
from loguru import logger
from pandas import DataFrame
from sqlglot import Expression, exp, parse

from .database_domain import Query, QueryType, Table
from .database_parameters import DatabaseParameters

if TYPE_CHECKING:
    from loguru import Logger


class DatabaseManager:
    """
    Manages the database operations for the Chess Reporter application.
    """

    DQL: ClassVar[tuple[type[exp.Expression], ...]] = (exp.Select,)
    DML: ClassVar[tuple[type[exp.Expression], ...]] = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Merge,
    )
    DDL: ClassVar[tuple[type[exp.Expression], ...]] = (
        exp.Create,
        exp.Alter,
        exp.Drop,
        exp.TruncateTable,
        exp.Comment,
        exp.Command,
    )
    DCL: ClassVar[tuple[type[exp.Expression], ...]] = (
        exp.Grant,
        exp.Revoke,
    )

    def __init__(self, internal: bool = False) -> None:
        """
        Initializes the DatabaseManager.

        Args:
            internal (bool):
                Whether the database manager is allowed to perform internal software operations.
        """
        self._logger: Logger = logger.bind(name="chess-reporter")
        self._parameters: DatabaseParameters = DatabaseParameters()
        self._connection: DuckDBPyConnection | None = None
        self._internal: bool = internal if isinstance(internal, bool) else False

    def __enter__(self) -> DatabaseManager:
        """
        Enables the use of the DatabaseManager as a context manager.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """
        Ensures that the database connection is properly closed when exiting the context.

        Args:
            exc_type (type[BaseException] | None):
                The type of the exception, if any, that caused the context to be exited.
            exc_value (BaseException | None):
                The exception instance, if any, that caused the context to be exited.
            traceback (TracebackType | None):
                The traceback object, if any, associated with the exception that caused the context
                to be exited.
        """
        self.close()

        return False

    def _connect(self) -> None:
        """
        Establishes a connection to the DuckDB database.
        """

        if self._connection is not None:
            return

        try:
            self._parameters.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            self._logger.exception(
                "Failed to create parent directory for database file `{}`", self._parameters.path
            )

            raise

        try:
            self._connection = connect(
                database=str(self._parameters.path),
                read_only=False,
                config=self._parameters.config,
            )
        except Exception:
            self._logger.exception("An error occurred while establishing the database connection")

            raise

    @property
    def connection(self) -> DuckDBPyConnection:
        """
        Provides access to the DuckDB database connection.
        """
        self._connect()

        if self._connection is None:
            error: str = "Database connection is not established"

            self._logger.error(error)

            raise RuntimeError(error)

        return self._connection

    def close(self) -> None:
        """
        Closes the database connection if it is established.
        """
        if self._connection is None:
            return

        try:
            self._connection.close()
        finally:
            self._connection = None

    def _get_query_type(self, expression: Expression) -> QueryType:
        """
        Determines the type of a SQL query based on its expression.

        Args:
            expression (Expression): The SQL expression to analyze for determining the query type.

        Returns:
            QueryType: An enumeration value representing the type of the SQL query.
        """
        if isinstance(expression, DatabaseManager.DCL):
            return QueryType.DCL

        if isinstance(expression, DatabaseManager.DDL):
            return QueryType.DDL

        if isinstance(expression, DatabaseManager.DML):
            return QueryType.DML

        if isinstance(expression, DatabaseManager.DQL):
            return QueryType.DQL

        sql: str = expression.sql(dialect="duckdb")
        error: str = f"Unsupported SQL query type for statement `{sql}`"

        self._logger.error(error)

        raise ValueError(error)

    def _execute_expression(self, query: Query) -> DataFrame | None:
        """
        Executes a SQL query represented by a Query object and returns the result
        as a pandas DataFrame if applicable.

        Args:
            query (Query): The Query object containing the SQL expression to be executed.

        Returns:
            DataFrame | None:
                A pandas DataFrame containing the results of the query if it is a DQL query,
                or None for other query types.
        """
        try:
            sql: str = query.sql

            self._logger.debug("Executing SQL\n{}", sql)

            if query.query_type == QueryType.DQL:
                dataframe: DataFrame = self.connection.execute(sql).fetchdf()

                return dataframe

            self.connection.execute(sql)

            return
        except Exception:
            self._logger.exception(
                "An error occurred while executing the SQL query on the database"
            )

            raise

    def _execute(self, sql: str) -> list[Query]:
        """
        Executes a raw SQL query on the database and returns a list of Query objects representing
        the executed queries, including their types, expressions, and result data if applicable.

        Args:
            sql (str): A valid SQL query string to be executed on the database.

        Returns:
            list[Query]:
                A list of Query objects representing the executed SQL statements, including
                their types, expressions, and result data if applicable.
        """
        if not isinstance(sql, str) or sql.strip() == "":
            error: str = "SQL query must be a valid non-empty string."

            self._logger.error(error)

            raise ValueError(error)

        try:
            expressions: list[Expression | None] = parse(sql=sql, dialect="duckdb")

            if len(expressions) == 0:
                error: str = "Failed to parse SQL query: No valid SQL statements found."

                self._logger.error(error)

                raise ValueError(error)

            queries: list[Query] = []

            for expression in expressions:
                if expression is None:
                    error: str = "Failed to parse SQL query: Invalid SQL statement found."

                    self._logger.error(error)

                    raise ValueError(error)

                query_type: QueryType = self._get_query_type(expression)
                query: Query = Query(query_type=query_type, expression=expression)
                dataframe_input: DataFrame | None = self._execute_expression(query=query)
                query.dataframe_input = dataframe_input

                queries.append(query)

            return queries
        except Exception:
            self._logger.exception("Failed to parse SQL query `{}`", sql)

            raise

    def execute(self, sql: str) -> list[Query]:
        """
        Executes a raw SQL query on the database and returns a list of Query objects representing
        the executed queries, including their types, expressions, and result data if applicable.

        Args:
            sql (str): A valid SQL query string to be executed on the database.

        Returns:
            list[Query]:
                A list of Query objects representing the executed SQL statements, including
                their types, expressions, and result data if applicable.
        """
        return self._execute(sql)

    def query(self, sql: str) -> Query:
        """
        Executes a raw SQL query on the database and returns a single Query object representing
        the executed query, including its type, expression, and result data if applicable.

        Args:
            sql (str): A valid SQL query string to be executed on the database.

        Returns:
            Query:
                A Query object representing the executed SQL statement, including its type,
                expression, and result data if applicable.
        """
        queries: list[Query] = self._execute(sql)

        if len(queries) == 0:
            error: str = "Failed to execute SQL query: No valid SQL statements found."

            self._logger.error(error)

            raise ValueError(error)

        if len(queries) > 1:
            error: str = "Failed to execute SQL query: Multiple SQL statements found."

            self._logger.error(error)

            raise ValueError(error)

        return queries[0]

    def _normalize_input(
        self,
        data: DataFrame | list[dict[str, Any]] | dict[str, Any],
        table: Table | str,
    ) -> tuple[DataFrame, Table]:
        """
        Normalizes the data and table inputs into a DataFrame and a Table object.

        Args:
            data (DataFrame | list[dict[str, Any]] | dict[str, Any]):
                Input data in one of the accepted formats.
            table (Table | str):
                Target table as a Table object or a `schema.table` string.

        Returns:
            tuple[DataFrame, Table]: Normalized DataFrame and Table object.
        """
        table_object: Table = table if isinstance(table, Table) else Table(table)

        if isinstance(data, DataFrame):
            return data, table_object

        if isinstance(data, list) and all(isinstance(row, dict) for row in data):
            return DataFrame(data), table_object

        if isinstance(data, dict):
            return DataFrame([data]), table_object

        error: str = (
            "Data must be a valid non-empty DataFrame, a list of dictionaries, or a single "
            "dictionary representing a row of data."
        )

        self._logger.error(error)

        raise ValueError(error)

    def _register_dataframe(self, dataframe: DataFrame, table: Table) -> str:
        """
        Registers a pandas DataFrame as a temporary table in the DuckDB database and returns the
        temporary table name.

        Args:
            dataframe (DataFrame):
                A pandas DataFrame containing the data to be registered as a temporary table
                in the DuckDB database.
            table (Table):
                A Table object representing the target table for the DataFrame, used to determine
                the temporary table name and validate the operation.

        Returns:
            str:
                The name of the temporary table in the DuckDB database where the DataFrame
                has been registered.
        """
        if not isinstance(dataframe, DataFrame) or dataframe.empty:
            error: str = "DataFrame must be a valid non-empty pandas DataFrame."

            self._logger.error(error)

            raise ValueError(error)

        tmp_name: str = table.temp_name

        try:
            self.connection.register(tmp_name, dataframe)
        except Exception:
            self._logger.exception("An error occurred while registering the DataFrame.")

            raise

        return tmp_name

    def _create_table(self, dataframe: DataFrame, table: Table, replace: bool = False) -> None:
        """
        Creates a new table in the DuckDB database from a pandas DataFrame, with an option to
        replace the table if it already exists.

        Args:
            dataframe (DataFrame):
                A pandas DataFrame containing the data to be used for creating the new table
                in the DuckDB database.
            table (Table):
                A Table object representing the target table to be created in the DuckDB database,
                used to determine the table name and validate the operation.
            replace (bool):
                A boolean flag indicating whether to replace the table if it already exists.
                Defaults to False.
        """
        if table.is_internal:
            error: str = "Forbidden table operation: cannot create internal tables."

            self._logger.error(error)

            raise ValueError(error)

        tmp_name: str = self._register_dataframe(dataframe, table)

        try:
            create_sql: str = f"""
                 CREATE {"OR REPLACE" if replace else ""} TABLE
                 {"IF NOT EXISTS" if not replace else ""} {table} AS
                 SELECT * FROM {tmp_name}
            """.strip()

            self.connection.execute(create_sql)
        except Exception:
            self._logger.exception("An error occurred while creating the table in the database.")

            raise
        finally:
            try:
                self.connection.unregister(tmp_name)
            except Exception:
                pass

    def _merge_dataframe(self, dataframe: DataFrame, table: Table) -> None:
        """
        Merges a pandas DataFrame into an existing table in the DuckDB database using a SQL MERGE
        statement, based on the presence of matching records in the target table.

        Args:
            dataframe (DataFrame):
                A pandas DataFrame containing the data to be merged into the
                target table in the DuckDB database.
            table (Table):
                A Table object representing the target table for the merge operation,
                used to determine the temporary table name and validate the operation.
        """
        if not table.is_internal or not self._internal:
            error: str = (
                "Forbidden table operation: merge operation is only allowed for internal tables."
            )

            self._logger.error(error)

            raise ValueError(error)

        tmp_name: str = self._register_dataframe(dataframe, table)

        try:
            columns: list[str] = dataframe.columns.tolist()
            set_clause: str = (
                ", ".join(
                    [
                        f"{column_name} = s.{column_name}"
                        for column_name in columns
                        if column_name not in {"id", "created_at", "updated_at"}
                    ]
                )
                + ", updated_at = CURRENT_TIMESTAMP"
            )
            insert_clause: str = ", ".join(
                [
                    f"{column_name}"
                    for column_name in columns
                    if column_name not in {"created_at", "updated_at"}
                ]
            )
            values_clause: str = ", ".join(
                [
                    f"s.{column_name}"
                    for column_name in columns
                    if column_name not in {"created_at", "updated_at"}
                ]
            )
            merge_sql: str = f"""
                MERGE INTO {str(table)} AS t
                USING {tmp_name} AS s
                ON t.id = s.id
                WHEN MATCHED THEN
                    UPDATE SET
                        {set_clause}
                WHEN NOT MATCHED THEN
                    INSERT
                        ({insert_clause})
                    VALUES
                        ({values_clause})
            """.strip()
            self.connection.execute(merge_sql)
        except Exception:
            self._logger.exception(
                "An error occurred while merging the DataFrame into the database table."
            )

            raise
        finally:
            try:
                self.connection.unregister(tmp_name)
            except Exception:
                pass

    def _insert_dataframe(self, dataframe: DataFrame, table: Table) -> None:
        """
        Inserts a pandas DataFrame into an existing table in the DuckDB database.

        Args:
            dataframe (DataFrame):
                A pandas DataFrame containing the data to be inserted into the target table
                in the DuckDB database.
            table (Table):
                A Table object representing the target table for the insert operation,
                used to determine the temporary table name and validate the operation.
        """
        if table.is_internal:
            error: str = (
                "Forbidden table operation: insert operation is not allowed for internal tables."
            )

            self._logger.error(error)

            raise ValueError(error)

        tmp_name: str = self._register_dataframe(dataframe, table)

        try:
            columns: list[str] = dataframe.columns.tolist()
            insert_sql: str = f"""
                INSERT INTO {str(table)} ({", ".join(columns)})
                SELECT {", ".join(columns)}
                FROM {tmp_name}
            """.strip()
            self.connection.execute(insert_sql)
        except Exception:
            self._logger.exception(
                "An error occurred while inserting the DataFrame into the database table."
            )

            raise
        finally:
            try:
                self.connection.unregister(tmp_name)
            except Exception:
                pass

    @overload
    def create_table(self, data: DataFrame, table: Table, replace: bool = False) -> None: ...

    @overload
    def create_table(self, data: DataFrame, table: str, replace: bool = False) -> None: ...

    @overload
    def create_table(
        self, data: list[dict[str, Any]], table: Table, replace: bool = False
    ) -> None: ...

    @overload
    def create_table(
        self, data: list[dict[str, Any]], table: str, replace: bool = False
    ) -> None: ...

    @overload
    def create_table(self, data: dict[str, Any], table: Table, replace: bool = False) -> None: ...

    @overload
    def create_table(self, data: dict[str, Any], table: str, replace: bool = False) -> None: ...

    @overload
    def merge(self, data: DataFrame, table: Table) -> None: ...

    @overload
    def merge(self, data: DataFrame, table: str) -> None: ...

    @overload
    def merge(self, data: list[dict[str, Any]], table: Table) -> None: ...

    @overload
    def merge(self, data: list[dict[str, Any]], table: str) -> None: ...

    @overload
    def merge(self, data: dict[str, Any], table: Table) -> None: ...

    @overload
    def merge(self, data: dict[str, Any], table: str) -> None: ...

    @overload
    def insert(self, data: DataFrame, table: Table) -> None: ...

    @overload
    def insert(self, data: DataFrame, table: str) -> None: ...

    @overload
    def insert(self, data: list[dict[str, Any]], table: Table) -> None: ...

    @overload
    def insert(self, data: list[dict[str, Any]], table: str) -> None: ...

    @overload
    def insert(self, data: dict[str, Any], table: Table) -> None: ...

    @overload
    def insert(self, data: dict[str, Any], table: str) -> None: ...

    def create_table(
        self,
        data: DataFrame | list[dict[str, Any]] | dict[str, Any],
        table: Table | str,
        replace: bool = False,
    ) -> None:
        """
        Creates a new table in the DuckDB database from the provided data, which can be in the
        form of a pandas DataFrame, a list of dictionaries, or a single dictionary representing
        a row of data. The method also accepts an option to replace the table if it already exists.

        Args:
            data (DataFrame | list[dict[str, Any]] | dict[str, Any]):
                The data to be used for creating the new table in the DuckDB database, which can
                be provided in one of the following formats:
                    - A pandas DataFrame containing multiple rows of data.
                    - A list of dictionaries, where each dictionary represents a row of data.
                    - A single dictionary representing a single row of data.
            table (Table | str):
                The target table to be created in the DuckDB database, which can be provided as
                either a Table object or the name of the table as a string.
            replace (bool):
                A boolean flag indicating whether to replace the table if it already exists.
                Defaults to False.
        """
        dataframe: DataFrame
        table_object: Table
        dataframe, table_object = self._normalize_input(data, table)

        self._create_table(dataframe, table_object, replace)

    def merge(
        self, data: DataFrame | list[dict[str, Any]] | dict[str, Any], table: Table | str
    ) -> None:
        """
        Merges data into a specified table in the DuckDB database, accepting various formats of
        input data.

        This method is designed to handle different types of input data for merging, including
        pandas DataFrames, lists of dictionaries, and single dictionaries representing rows of
        data. It validates the input data format and delegates the merging process to the
        appropriate helper methods based on the type of the input data.

        Args:
            data (DataFrame | list[dict[str, Any]] | dict[str, Any]):
                The data to be merged into the database, which can be provided in one of the
                following formats:
                    - A pandas DataFrame containing multiple rows of data.
                    - A list of dictionaries, where each dictionary represents a row of data.
                    - A single dictionary representing a single row of data.
            table (Table | str):
                The target table in the database where the data should be merged. This can be
                either a Table object or the name of the table as a string.
        """
        dataframe: DataFrame
        table_object: Table
        dataframe, table_object = self._normalize_input(data, table)

        self._merge_dataframe(dataframe, table_object)

    def insert(
        self, data: DataFrame | list[dict[str, Any]] | dict[str, Any], table: Table | str
    ) -> None:
        """
        Inserts data into a specified table in the DuckDB database, accepting various formats of
        input data.

        This method is designed to handle different types of input data for insertion, including
        pandas DataFrames, lists of dictionaries, and single dictionaries representing rows of
        data. It validates the input data format and delegates the insertion process to the
        appropriate helper methods based on the type of the input data.

        Args:
            data (DataFrame | list[dict[str, Any]] | dict[str, Any]):
                The data to be inserted into the database, which can be provided in one of the
                following formats:
                    - A pandas DataFrame containing multiple rows of data.
                    - A list of dictionaries, where each dictionary represents a row of data.
                    - A single dictionary representing a single row of data.
            table (Table | str):
                The target table in the database where the data should be inserted. This can be
                either a Table object or the name of the table as a string.
        """
        dataframe: DataFrame
        table_object: Table
        dataframe, table_object = self._normalize_input(data, table)

        self._insert_dataframe(dataframe, table_object)
