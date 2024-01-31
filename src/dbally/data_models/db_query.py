from dataclasses import dataclass


@dataclass
class QueryResult:
    """Class for storing query execution results."""

    sql_query: str
    execution_time: float
    rows: list
