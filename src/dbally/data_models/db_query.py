from dataclasses import dataclass
from typing import List, Sequence, Union


@dataclass
class QueryResult:
    """Class for storing query execution results."""

    sql_query: str
    execution_time: float
    rows: Union[Sequence, List]
