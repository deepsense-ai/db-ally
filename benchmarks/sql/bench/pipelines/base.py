from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from omegaconf import DictConfig

from dbally.context import Context
from dbally.iql._exceptions import IQLError
from dbally.iql._query import IQLQuery
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.clients.exceptions import LLMError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM

from ..contexts import CONTEXTS_REGISTRY


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
    def from_query(cls, query: Optional[Union[IQLQuery, BaseException]]) -> "IQL":
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

    def __init__(self, config: DictConfig) -> None:
        super().__init__()
        self.contexts = self.get_contexts(config.setup)

    def get_llm(self, config: DictConfig) -> LLM:
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

    def get_contexts(self, config: DictConfig) -> List[Context]:
        """
        Returns the contexts based on the configuration.

        Args:
            config: The contexts configuration.

        Returns:
            The contexts.
        """
        return [CONTEXTS_REGISTRY[context]() for contexts in config.contexts.values() for context in contexts]

    @abstractmethod
    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
