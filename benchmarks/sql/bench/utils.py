import time
from typing import Any, Dict, List, Tuple

from sqlalchemy import Engine, text


def execute_query(query: str, engine: Engine) -> Tuple[List[Dict[str, Any]], float]:
    """
    Execute the given query on the database.

    Args:
        query: The query to be executed.
        engine: The database engine.

    Returns:
        The query results.
    """
    with engine.connect() as connection:
        start_time = time.perf_counter()
        rows = connection.execute(text(query)).fetchall()
        execution_time = time.perf_counter() - start_time
    return [dict(row._mapping) for row in rows], execution_time  # pylint: disable=protected-access


def avarage_execution_time(query: str, engine: Engine, n: int) -> float:
    """
    Execute the given query on the database n times and return the average execution time.

    Args:
        query: The query to be executed.
        engine: The database engine.
        n: The number of times to execute the query.

    Returns:
        The average execution time.
    """
    return sum(execute_query(query, engine)[1] for _ in range(n)) / n
