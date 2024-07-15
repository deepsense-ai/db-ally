import json
import sys
import time
from datetime import datetime
from pathlib import Path
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


def save(file_path: Path, **data: Any) -> None:
    """
    Save the data to a file. Add the current timestamp and Python version to the data.

    Args:
        file_path: The path to the file.
        data: The data to be saved.
    """
    current_time = datetime.now()

    data["_timestamp"] = current_time.isoformat()
    data["_python_version"] = sys.version
    data["_interpreter_path"] = sys.executable

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
