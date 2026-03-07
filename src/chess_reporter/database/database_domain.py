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

    @property
    def has_data(self) -> bool:
        """
        Indicates whether the query type is a Data Query Language (DQL) query.
        """
        return self == QueryType.DQL


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
    data: Optional[DataFrame] = Field(
        default=None, description="Pandas DataFrame result of the query, if applicable"
    )

    @property
    def sql(self) -> str:
        """
        SQL string representation of the query expression.
        """
        return self.expression.sql(dialect="duckdb")

    @property
    def raw_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        List of dictionaries of data (instead of a Pandas DataFrame).
        """
        if self.data is not None:
            pandas_data: List[Dict[Hashable, Any]] = self.data.to_dict(orient="records")
            converted_data: List[Dict[str, Any]] = [
                {str(key): value for key, value in record.items()} for record in pandas_data
            ]

            return converted_data.copy()

        return None

    @field_serializer("expression")
    def serialize_expression(self, expression: Expression) -> str:
        """
        Serializes the SQL expression.
        """
        return self.sql

    @field_serializer("data")
    def serialize_data(self, data: Optional[DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """
        Serializes the DataFrame.
        """
        if data is not None:
            return self.raw_data

        return None
