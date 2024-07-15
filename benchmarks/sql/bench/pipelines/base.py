from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from datasets import Dataset

from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM


@dataclass
class ExecutionResult:
    """
    Represents the result of a single query execution.
    """

    sql: Optional[str] = None
    iql: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    exception: Optional[Exception] = None
    execution_time: Optional[float] = None


@dataclass
class EvaluationResult:
    """
    Represents the result of a single evaluation.
    """

    question: str
    reference: ExecutionResult
    prediction: ExecutionResult
    db_url: Optional[str] = None

    dict = asdict


class EvaluationPipeline(ABC):
    """
    Evaluation pipeline base class.
    """

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
    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the evaluation pipeline.

        Args:
            dataset: The evaluation dataset.

        Returns:
            The list of evaluation results.
        """
