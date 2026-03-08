"""
Database manager for the Chess Reporter application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, overload

from duckdb import DuckDBPyConnection, connect
from loguru import logger
from pandas import DataFrame
from sqlglot import Expression, exp, parse

from chess_reporter.database.database_domain import Query, QueryType
from chess_reporter.database.database_parameters import DatabaseParameters

if TYPE_CHECKING:
    from loguru import Logger


class DatabaseManager:
    """
    Manages the connection to the DuckDB database.

    Methods:
        connection: Provides access to the DuckDB database connection.
        close: Closes the database connection if it is established.
        execute: Executes a raw SQL query on the database and returns a list of Query objects
            representing the executed queries, including their types, expressions, and result data
            if applicable.
        insert_data: Inserts data into a specified table in the DuckDB database, accepting
            various formats of input data, including pandas DataFrames, lists of dictionaries, and
            single dictionaries representing rows of data.
    """

    def __init__(self) -> None:
        """
        Initializes the DatabaseManager.
        """
        self.__parameters: DatabaseParameters = DatabaseParameters()
        self.__connection: Optional[DuckDBPyConnection] = None
        self.__logger: Logger = logger.bind(name="chess-reporter")

    def __connect(self) -> None:
        """
        Establishes a connection to the DuckDB database.
        """

        if self.__connection is not None:
            return

        try:
            self.__parameters.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.__logger.exception(
                "Failed to create parent directory for database file `{}`", self.__parameters.path
            )
            raise

        try:
            self.__connection = connect(
                database=str(self.__parameters.path),
                read_only=False,
                config=self.__parameters.config,
            )
        except Exception:
            self.__logger.exception("An error occurred while establishing the database connection")
            raise

    @property
    def connection(self) -> DuckDBPyConnection:
        """
        Provides access to the DuckDB database connection.
        """
        self.__connect()

        if self.__connection is None:
            error: str = "Database connection is not established"

            self.__logger.error(error)
            raise RuntimeError(error)

        return self.__connection

    def close(self) -> None:
        """
        Closes the database connection if it is established.
        """
        if self.__connection is None:
            return

        try:
            self.__connection.close()
        except Exception:
            pass

    def __get_query_type(self, expression: Expression) -> QueryType:
        """
        Determines the type of a SQL query based on its expression.

        Args:
            expression (Expression): The SQL expression to analyze for determining the query type.

        Returns:
            QueryType: An enumeration value representing the type of the SQL query.
        """
        DQL = (exp.Select,)
        DML = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Merge,
        )
        DDL = (exp.Create, exp.Alter, exp.Drop, exp.TruncateTable, exp.Comment, exp.Command)
        DCL = (
            exp.Grant,
            exp.Revoke,
        )

        if isinstance(expression, DCL):
            return QueryType.DCL
        elif isinstance(expression, DDL):
            return QueryType.DDL
        elif isinstance(expression, DML):
            return QueryType.DML
        elif isinstance(expression, DQL):
            return QueryType.DQL
        else:
            sql: str = expression.sql(dialect="duckdb")
            error: str = "Unsupported SQL query type for statement `{}`" % sql

            self.__logger.error(error)
            raise ValueError(error)

    def __execute_expression(self, query: Query) -> Optional[DataFrame]:
        """
        Executes a SQL query represented by a Query object and returns the result
        as a pandas DataFrame if applicable.

        Args:
            query (Query): The Query object containing the SQL expression to be
                executed.

        Returns:
            Optional[DataFrame]: A pandas DataFrame containing the results of the
                query if it is a DQL query, or None for other query types.
        """
        try:
            sql: str = query.sql

            self.__logger.debug("Executing SQL\n{}", sql)

            if query.query_type == QueryType.DQL:
                result: DataFrame = self.connection.execute(sql).fetchdf()

                return result
            else:
                self.connection.execute(sql)

                return
        except Exception:
            self.__logger.exception(
                "An error occurred while executing the SQL query on the database"
            )
            raise

    def execute(self, sql: str) -> List[Query]:
        """
        Executes a raw SQL query on the database and returns a list of Query objects representing
        the executed queries, including their types, expressions, and result data if applicable.

        The method parses the input SQL string, determines the type of each query, executes them on
        the database, and collects the results in a structured format for further processing.

        Args:
            sql (str): A valid SQL query string to be executed on the database.

        Returns:
            List[Query]: A list of Query objects representing the executed queries, where each Query
                object contains the query type, SQL expression, and result data if applicable.
        """
        if not isinstance(sql, str) or sql.strip() == "":
            error: str = "SQL query must be a valid non-empty string."

            self.__logger.error(error)
            raise ValueError(error)

        try:
            expressions: List[Optional[Expression]] = parse(sql=sql, dialect="duckdb")

            if len(expressions) == 0:
                error: str = "Failed to parse SQL query: No valid SQL statements found."

                self.__logger.error(error)
                raise ValueError(error)

            queries_statements: List[Query] = []

            for expression in expressions:
                if expression is None:
                    error: str = "Failed to parse SQL query: Invalid SQL statement found."

                    self.__logger.error(error)
                    raise ValueError(error)

                query_type: QueryType = self.__get_query_type(expression)
                query: Query = Query(query_type=query_type, expression=expression)
                data: Optional[DataFrame] = self.__execute_expression(query=query)
                query.data = data

                queries_statements.append(query)

            return queries_statements.copy()
        except Exception:
            self.__logger.exception("Failed to parse SQL query `{}`", sql)
            raise

    def __insert_df(self, table_name: str, df: DataFrame) -> None:
        """
        Inserts data from a pandas DataFrame into a specified table in the DuckDB database.

        Args:
            table_name (str):
                The name of the target table in the database where the data should be inserted.
            df (DataFrame):
                A pandas DataFrame containing the data to be inserted into the database.
        """
        if not isinstance(table_name, str) or table_name.strip() == "":
            error: str = "Table name must be a valid non-empty string."

            self.__logger.error(error)
            raise ValueError(error)

        if not isinstance(df, DataFrame) or df.empty:
            error: str = "DataFrame must be a valid non-empty pandas DataFrame."

            self.__logger.error(error)
            raise ValueError(error)

        try:
            rows_inserted: int = len(df)

            self.connection.append(table_name=table_name, df=df, by_name=True)

            self.__logger.info("Inserted {} rows into table `{}`", rows_inserted, table_name)
        except Exception:
            self.__logger.exception("An error occurred while inserting data into the database")
            raise

    def __insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Inserts data from a list of dictionaries into a specified table in the DuckDB database.

        Args:
            table_name (str):
                The name of the target table in the database where the data should be inserted.
            data (List[Dict[str, Any]]):
                A list of dictionaries, where each dictionary represents a row of data to be
                inserted into the database, with keys corresponding to column names and values
                corresponding to the data for those columns.
        """
        if not isinstance(data, list) or len(data) == 0:
            error: str = "Data must be a valid non-empty list of dictionaries."

            self.__logger.error(error)
            raise ValueError(error)

        if not all(isinstance(row, dict) for row in data):
            error: str = (
                "Data must be a list of dictionaries, where each dictionary represents a"
                " row of data."
            )

            self.__logger.error(error)
            raise ValueError(error)

        try:
            df: DataFrame = DataFrame(data)
            self.__insert_df(table_name=table_name, df=df)
        except Exception:
            self.__logger.exception("An error occurred while inserting data into the database")
            raise

    def __insert_row(self, table_name: str, row: Dict[str, Any]) -> None:
        """
        Inserts a single row of data, represented as a dictionary, into a specified table in the
            DuckDB database.

        Args:
            table_name (str):
                The name of the target table in the database where the data should be inserted.
            row (Dict[str, Any]):
                A dictionary representing a single row of data to be inserted into the database,
                with keys corresponding to column names and values corresponding to the data for
                those columns.
        """
        if not isinstance(row, dict) or len(row) == 0:
            error: str = "Row must be a valid non-empty dictionary."

            self.__logger.error(error)
            raise ValueError(error)

        try:
            self.__insert_data(table_name=table_name, data=[row])
        except Exception:
            self.__logger.exception("An error occurred while inserting data into the database")
            raise

    @overload
    def insert(self, table_name: str, data: DataFrame) -> None: ...

    @overload
    def insert(self, table_name: str, data: List[Dict[str, Any]]) -> None: ...

    @overload
    def insert(self, table_name: str, data: Dict[str, Any]) -> None: ...

    def insert(self, table_name: str, data: Any) -> None:
        """
        Inserts data into a specified table in the DuckDB database, accepting various formats of
        input data.

        This method is designed to handle different types of input data for insertion, including
        pandas DataFrames, lists of dictionaries, and single dictionaries representing rows of
        data. It validates the input data format and delegates the insertion process to the
        appropriate helper methods based on the type of the input data.

        Args:
            table_name (str):
                The name of the target table in the database where the data should be inserted.
            data (Union[DataFrame, List[Dict[str, Any]], Dict[str, Any]]):
                The data to be inserted into the database, which can be provided in one of the
                following formats:
                    - A pandas DataFrame containing multiple rows of data.
                    - A list of dictionaries, where each dictionary represents a row of data.
                    - A single dictionary representing a single row of data.
        """
        if isinstance(data, DataFrame):
            self.__insert_df(table_name, data)
        elif isinstance(data, list) and all(isinstance(row, dict) for row in data):
            self.__insert_data(table_name, data)
        elif isinstance(data, dict):
            self.__insert_row(table_name, data)
        else:
            error: str = (
                "Data must be a valid non-empty DataFrame, a list of dictionaries, or a single "
                "dictionary representing a row of data."
            )

            self.__logger.error(error)
            raise ValueError(error)
