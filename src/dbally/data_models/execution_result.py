from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ExecutionMetadata:
    """
    Represents the metadata of the query execution.
    """

    query: str
    execution_time: float


@dataclass
class ExecutionResult:
    """
    Represents the result of the query execution.
    """

    results: List[Dict[str, Any]]
    metadata: ExecutionMetadata
    answer: Optional[str] = None
