from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ViewExecutionResult:
    """
    Represents the result of the query execution for a single view.

    Args:
        results: List of dictionaries containing the results of the query execution,
            each dictionary represents a row in the result set with column names as keys.
        context: Dictionary containing addtional metadata about the query execution.
    """

    results: List[Dict[str, Any]]
    context: Dict[str, Any]


@dataclass
class ExecutionResult:
    """
    Represents the collection-level result of the query execution.

    Args:
        results: List of dictionaries containing the results of the query execution,
            each dictionary represents a row in the result set with column names as keys.
            The exact structure of the result set depends on the view that was used to execute the query,
            which can be obtained from the `view_name` attribute.
        context: Dictionary containing addtional metadata about the query execution.
        execution_time: Time taken to execute the entire query, including view selection
            and all other operations, in seconds.
        execution_time_view: Time taken that the selected view took to execute the query, in seconds.
        view_name: Name of the view that was used to execute the query.
        textual_response: Optional text response that can be used to display the query results
            in a human-readable format.
    """

    results: List[Dict[str, Any]]
    context: Dict[str, Any]
    execution_time: float
    execution_time_view: float
    view_name: str
    textual_response: Optional[str] = None
