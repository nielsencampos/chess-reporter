"""
Database package: domain module
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Hashable
from uuid import uuid4

from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_serializer, model_validator
from sqlglot import Expression


class QueryType(StrEnum):
    """
    Query Type

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
    Query
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    query_type: QueryType = Field(description="The type of the database query")
    expression: Expression = Field(description="The SQL expression representing the database query")
    dataframe_input: DataFrame | None = Field(
        default=None, description="The DataFrame input for the query, if applicable"
    )

    @property
    def sql(self) -> str:
        """
        SQL string representation
        """
        return self.expression.sql(dialect="duckdb")

    @property
    def dataframe(self) -> DataFrame:
        """
        DataFrame representation of the query result
        """
        if self.dataframe_input is None:
            raise ValueError("Data is not available as a DataFrame.")

        return self.dataframe_input

    @property
    def columns(self) -> list[str]:
        """
        List of column names
        """
        return self.dataframe.columns.tolist()

    @property
    def data(self) -> list[dict[str, Any]]:
        """
        List of dictionaries of data (instead of a Pandas DataFrame)
        """
        pandas_data: list[dict[Hashable, Any]] = self.dataframe.to_dict(orient="records")
        converted_data: list[dict[str, Any]] = [
            {str(key): value for key, value in record.items()} for record in pandas_data
        ]

        return converted_data

    @property
    def row(self) -> dict[str, Any]:
        """
        First row of the data
        """
        first_row = self.data[0] if len(self.data) > 0 else {}

        return first_row

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
        return expression.sql(dialect="duckdb")

    @field_serializer("dataframe_input")
    def serialize_data(self, dataframe_input: DataFrame | None) -> list[dict[str, Any]] | None:
        """
        Serializes the DataFrame.
        """
        return None if dataframe_input is None else self.data


class Table(RootModel[str]):
    """
    Table
    """

    @model_validator(mode="before")
    @classmethod
    def build_table(cls, value: str) -> str:
        """
        Validates and constructs the table in the format `schema.table`.
        """
        if not isinstance(value, str):
            raise ValueError("Table must be a string.")

        full_name: str = value.strip().lower()
        parts: list[str] = full_name.split(".")

        if len(parts) != 2:
            raise ValueError("Table must be in the format `schema.table`.")

        if any(not part.isidentifier() for part in parts):
            raise ValueError("Table components must be valid identifiers.")

        return full_name

    def __str__(self) -> str:
        """
        String representation of the table.
        """
        return self.root

    @property
    def parts(self) -> tuple[str, str]:
        """
        Returns the schema and table name as a tuple.
        """
        schema_name, table_name = self.root.split(".")

        return schema_name, table_name

    @property
    def schema_name(self) -> str:
        """
        Schema name
        """
        return self.parts[0]

    @property
    def table_name(self) -> str:
        """
        Table name
        """
        return self.parts[1]

    @property
    def is_internal(self) -> bool:
        """
        Checks if the table is an internal table (e.g., starts with "chess_reporter").
        """
        return self.schema_name == "chess_reporter"

    @property
    def temp_name(self) -> str:
        """
        Returns the table name formatted for temporary table registration (e.g., without schema).
        """
        return f"_tmp_{self.root.replace('.', '_')}_{uuid4().hex}"
