from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

import dbally
from dbally.collection.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM

from .views import VIEWS_REGISTRY


@dataclass
class ExecutionResult:
    """
    Represents the result of a single query execution.
    """

    iql: Optional[str] = None
    sql: Optional[str] = None
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
            "iql": self.iql,
            "sql": self.sql,
        }


@dataclass
class EvaluationResult:
    """
    Represents the result of a single evaluation.
    """

    question: str
    reference: ExecutionResult
    prediction: ExecutionResult
    db_url: Optional[str] = None

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


class EvaluationPipeline:
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.

        Raises:
            ValueError: If no valid views are found in the configuration.
        """
        self.db = create_engine(config.data.db_url)
        self.llm = self.get_llm(config.llm)
        self.collection = self.get_collection(config.setup)

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

    def get_collection(self, config: Dict) -> Collection:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.

        Raises:
            ValueError: If the view name is not supported.
        """
        collection = dbally.create_collection(config.name, self.llm)
        collection.n_retries = 0

        for view_name in config.views:
            view_cls = VIEWS_REGISTRY[view_name]
            collection.add(view_cls, lambda: view_cls(self.db))  # pylint: disable=cell-var-from-loop

        return collection

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
            try:
                result = await self.collection.ask(
                    question=data["question"],
                    dry_run=True,
                    return_natural_response=False,
                )
            except NoViewFoundError as exc:
                prediction = ExecutionResult(exception=exc)
            except IQLError as exc:
                prediction = ExecutionResult(iql=exc.source, exception=exc)
            except UnsupportedQueryError as exc:
                prediction = ExecutionResult(iql="UNSUPPORTED_QUERY", exception=exc)
            # TODO: Remove this exception handling once the Text2SQL view is fixed
            except Exception as exc:  # pylint: disable=broad-except
                prediction = ExecutionResult(exception=exc)
            else:
                prediction = ExecutionResult(
                    iql=result.context.get("iql", None),
                    sql=result.context.get("sql", None),
                )

            reference = ExecutionResult(
                iql=data["iql"],
                sql=data["sql"],
            )
            result = EvaluationResult(
                question=data["question"],
                reference=reference,
                prediction=prediction,
                db_url=str(self.db.url),
            )
            results.append(result)

        return results
