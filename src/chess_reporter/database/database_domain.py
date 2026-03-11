"""
Database domain definitions for the Chess Reporter application.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Dict, Hashable, List, Optional

from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from sqlglot import Expression


class QueryType(StrEnum):
    """
    Enumeration of query types for the Chess Reporter application.

    Values:
        DQL: Represents a Data Query Language query (e.g., SELECT).
        DML: Represents a Data Manipulation Language query (e.g., INSERT, UPDATE, DELETE).
        DDL: Represents a Data Definition Language query (e.g., CREATE, ALTER, DROP).
        DCL: Represents a Data Control Language query (e.g., GRANT, REVOKE).
    """

    DQL = "dql"
    DML = "dml"
    DDL = "ddl"
    DCL = "dcl"


class Query(BaseModel):
    """
    Represents a database query in the Chess Reporter application.

    Attributes:
        query_type (QueryType): The type of the database query.
        expression (Expression): The SQL expression representing the database query.
        data (Optional[DataFrame]): Pandas DataFrame result of the query, if applicable.

    Properties:
        sql (str):
            SQL string representation of the query expression.
        raw_data (Optional[List[Dict[str, Any]]]):
            List of dictionaries of data (instead of a Pandas DataFrame).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    query_type: QueryType = Field(description="The type of the database query")
    expression: Expression = Field(description="The SQL expression representing the database query")
    data_returned: Optional[DataFrame] = Field(
        default=None, description="Pandas DataFrame result of the query, if applicable"
    )

    @property
    def sql(self) -> str:
        """
        SQL string representation
        """
        return self.expression.sql(dialect="duckdb")

    @property
    def data(self) -> DataFrame:
        """
        DataFrame result
        """
        if self.data_returned is None:
            raise ValueError("Data is not available as a DataFrame.")

        return self.data_returned.copy()

    @property
    def columns(self) -> List[str]:
        """
        List of column names
        """
        return self.data.columns.tolist().copy()

    @property
    def raw_data(self) -> List[Dict[str, Any]]:
        """
        List of dictionaries of data (instead of a Pandas DataFrame)
        """
        pandas_data: List[Dict[Hashable, Any]] = self.data.to_dict(orient="records")
        converted_data: List[Dict[str, Any]] = [
            {str(key): value for key, value in record.items()} for record in pandas_data
        ]

        return converted_data.copy()

    @property
    def row(self) -> Dict[str, Any]:
        """
        First row of the data
        """
        first_row = self.raw_data[0] if len(self.raw_data) > 0 else {}

        return first_row.copy()

    @property
    def value(self) -> Any:
        """
        First value of the first row of the data
        """
        first_row = self.row
        first_value = next(iter(first_row.values()), None)

        return first_value

    @field_serializer("expression")
    def serialize_expression(self, expression: Expression) -> str:
        """
        Serializes the SQL expression
        """
        return self.sql

    @field_serializer("data_returned")
    def serialize_data(self, data_returned: Optional[DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """
        Serializes the DataFrame.
        """
        if data_returned is None:
            return None

        return self.raw_data.copy()
