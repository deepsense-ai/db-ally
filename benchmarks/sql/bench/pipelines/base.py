from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine

from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM


@dataclass
class IQLResult:
    """
    Represents the IQL result.
    """

    filters: Optional[str] = None
    aggregation: Optional[str] = None

    def __eq__(self, other: "IQLResult") -> bool:
        """
        Compares two IQL results.

        Args:
            other: The other IQL result to compare.

        Returns:
            True if the two IQL results are equal, False otherwise.
        """
        return self.filters == other.filters and self.aggregation == other.aggregation

    def dict(self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of the object.

        Returns:
            The dictionary representation.
        """
        return {
            "filters": self.filters,
            "aggregation": self.aggregation,
        }


@dataclass
class ExecutionResult:
    """
    Represents the result of a single query execution.
    """

    view: Optional[str] = None
    sql: Optional[str] = None
    iql: Optional[IQLResult] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    exception: Optional[Exception] = None
    execution_time: Optional[float] = None

    def dict(self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of the object.

        Returns:
            The dictionary representation.
        """
        return {
            "view": self.view,
            "iql": self.iql.dict() if self.iql else None,
            "sql": self.sql,
            "len_results": len(self.results),
        }


@dataclass
class EvaluationResult:
    """
    Represents the result of a single evaluation.
    """

    question: str
    reference: ExecutionResult
    prediction: ExecutionResult

    def dict(self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of the object.

        Returns:
            The dictionary representation.
        """
        return {
            "question": self.question,
            "reference": self.reference.dict(),
            "prediction": self.prediction.dict(),
        }


class EvaluationPipeline(ABC):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        self.db = create_engine(config.data.db_url)

    def get_llm(self, config: Dict) -> LLM:
        """
        Returns the LLM based on the configuration.

        Args:
            config: The LLM configuration.

        Returns:
            The LLM object.
        """
        if config.model_name.startswith("local/"):
            return LocalLLM(config.model_name.split("/", 1)[1])
        return LiteLLM(config.model_name)

    @abstractmethod
    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
