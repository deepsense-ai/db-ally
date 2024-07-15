from abc import ABC
from typing import Dict, List

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.views.base import BaseView
from dbally.views.freeform.text2sql.exceptions import Text2SQLError

from ..views import FREEFORM_VIEWS_REGISTRY, STRUCTURED_VIEWS_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult


class ViewEvaluationPipeline(EvaluationPipeline, ABC):
    """
    Pipeline for evaluating views.
    """

    VIEWS_REGISTRY: Dict[str, BaseView] = {}

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.

        Raises:
            ValueError: If the view name is not supported.
        """
        self.llm = self.get_llm(config.llm)
        self.view, self.db_url = self.get_view(config.data.views)

    def get_view(self, config: Dict) -> BaseView:
        """
        Returns the view object based on the configuration.

        Args:
            config: The view configuration.

        Returns:
            The view object, and the database URL.

        Raises:
            ValueError: If the view name is not supported.
        """
        view_name, db_url = next(
            ((view, db_url) for view, db_url in config.items() if view in self.VIEWS_REGISTRY),
            (None, None),
        )
        if not view_name:
            raise ValueError(f"No views found in the configuration. Supported views: {list(self.VIEWS_REGISTRY)}.")
        view_cls = self.VIEWS_REGISTRY[view_name]
        return view_cls(create_engine(db_url)), db_url

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        results = []

        for data in tqdm(dataset, desc="Evaluation"):
            try:
                result = await self.view.ask(
                    query=data["question"],
                    llm=self.llm,
                    n_retries=0,
                    dry_run=True,
                )
            except IQLError as exc:
                prediction = ExecutionResult(iql=exc.source, exception=exc)
            except UnsupportedQueryError as exc:
                prediction = ExecutionResult(exception=exc)
            except Text2SQLError as exc:
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
                db_url=self.db_url,
            )
            results.append(result)

        return results


class IQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Pipeline for evaluating structured views.
    """

    VIEWS_REGISTRY = STRUCTURED_VIEWS_REGISTRY


class SQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Pipeline for evaluating freeform views.
    """

    VIEWS_REGISTRY = FREEFORM_VIEWS_REGISTRY
