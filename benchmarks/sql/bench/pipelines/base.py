from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from dbally.iql._exceptions import IQLError
from dbally.iql._query import IQLQuery
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.clients.exceptions import LLMError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM


@dataclass
class IQL:
    """
    Represents the IQL.
    """

    source: Optional[str] = None
    unsupported: bool = False
    valid: bool = True
    generated: bool = True

    @classmethod
    def from_query(cls, query: Optional[Union[IQLQuery, Exception]]) -> "IQL":
        """
        Creates an IQL object from the query.

        Args:
            query: The IQL query or exception.

        Returns:
            The IQL object.
        """
        return cls(
            source=query.source if isinstance(query, (IQLQuery, IQLError)) else None,
            unsupported=isinstance(query, UnsupportedQueryError),
            valid=not isinstance(query, IQLError),
            generated=not isinstance(query, LLMError),
        )


@dataclass
class IQLResult:
    """
    Represents the result of an IQL query execution.
    """

    filters: IQL
    aggregation: IQL
    context: bool = False


@dataclass
class ExecutionResult:
    """
    Represents the result of a single query execution.
    """

    view_name: Optional[str] = None
    iql: Optional[IQLResult] = None
    sql: Optional[str] = None


@dataclass
class EvaluationResult:
    """
    Represents the result of a single evaluation.
    """

    db_id: str
    question_id: str
    question: str
    reference: ExecutionResult
    prediction: ExecutionResult


class EvaluationPipeline(ABC):
    """
    Collection evaluation pipeline.
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
    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
