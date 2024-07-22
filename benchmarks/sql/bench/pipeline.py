from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from .views import VIEWS_REGISTRY


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

    @abstractmethod
    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the evaluation pipeline.

        Args:
            dataset: The evaluation dataset.

        Returns:
            The list of evaluation results.
        """


class ViewEvaluationPipeline(EvaluationPipeline, ABC):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.llm = self.get_llm(config.setup.llm)

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


class IQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.views = self.get_views(config.setup)

    def get_views(self, config: Dict) -> Dict[str, Type[SqlAlchemyBaseView]]:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.
        """
        return {view: VIEWS_REGISTRY[view] for view in config.views}

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the evaluation pipeline.

        Args:
            dataset: The evaluation dataset.

        Returns:
            The list of evaluation results.
        """
        results = []

        for data in tqdm(dataset, desc="Evaluation"):
            view = self.views[data["view"]](self.db)
            try:
                result = await view.ask(
                    query=data["question"],
                    llm=self.llm,
                    dry_run=True,
                    n_retries=0,
                )
            # TODO: Refactor exception handling for IQLError for filters and aggregation
            except IQLError as exc:
                prediction = ExecutionResult(
                    view=data["view"],
                    iql=IQLResult(filters=exc.source),
                    exception=exc,
                )
            except (UnsupportedQueryError, Exception) as exc:  # pylint: disable=broad-except
                prediction = ExecutionResult(
                    view=data["view"],
                    exception=exc,
                )
            else:
                prediction = ExecutionResult(
                    view=data["view"],
                    iql=IQLResult(filters=result.context["iql"]),
                    sql=result.context["sql"],
                )

            reference = ExecutionResult(
                view=data["view"],
                iql=IQLResult(
                    filters=data["iql_filters"],
                    aggregation=data["iql_aggregation"],
                ),
                sql=data["sql"],
            )
            result = EvaluationResult(
                question=data["question"],
                reference=reference,
                prediction=prediction,
            )
            results.append(result)

        return results


class SQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.view = self.get_view(config.setup)

    def get_view(self, config: Dict) -> Type[BaseText2SQLView]:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.
        """
        return VIEWS_REGISTRY[config.view]

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the evaluation pipeline.

        Args:
            dataset: The evaluation dataset.

        Returns:
            The list of evaluation results.
        """
        results = []

        for data in tqdm(dataset, desc="Evaluation"):
            view = self.view(self.db)

            try:
                result = await view.ask(
                    query=data["question"],
                    llm=self.llm,
                    dry_run=True,
                    n_retries=0,
                )
            # TODO: Remove this broad exception handling once the Text2SQL view is fixed
            except Exception as exc:  # pylint: disable=broad-except
                prediction = ExecutionResult(
                    view=self.view.__name__,
                    exception=exc,
                )
            else:
                prediction = ExecutionResult(
                    view=self.view.__name__,
                    sql=result.context["sql"],
                )

            reference = ExecutionResult(
                view=data["view"],
                sql=data["sql"],
            )
            result = EvaluationResult(
                question=data["question"],
                reference=reference,
                prediction=prediction,
            )
            results.append(result)

        return results
