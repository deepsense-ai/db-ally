from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionResult:
    """
    Represents the result of the query execution.
    """

    results: List[Dict[str, Any]]
    context: Dict[str, Any]
    textual_response: Optional[str] = None
    execution_time: Optional[float] = None
