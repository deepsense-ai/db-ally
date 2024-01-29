from pydantic import BaseModel


class QueryResult(BaseModel):
    """Class for storing query execution results."""

    sql_query: str
    execution_time: float
    rows: list
