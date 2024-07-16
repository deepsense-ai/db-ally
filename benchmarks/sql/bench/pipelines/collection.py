from typing import Dict, List

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

import dbally
from dbally.collection.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.views.freeform.text2sql.exceptions import Text2SQLError
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import FREEFORM_VIEWS_REGISTRY, STRUCTURED_VIEWS_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult


class CollectionEvaluationPipeline(EvaluationPipeline):
    """
    Pipeline for evaluating IQL predictions.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.

        Raises:
            ValueError: If the view name is not supported.
        """
        self.llm = self.get_llm(config.llm)
        self.collection = self.get_collection(config.data.views)

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
        if not config:
            raise ValueError("No structured or freeform views found in the configuration.")

        collection = dbally.create_collection("bench", self.llm)
        collection.n_retries = 0

        for view_name, db_url in config.items():
            if view_cls := STRUCTURED_VIEWS_REGISTRY.get(view_name) or FREEFORM_VIEWS_REGISTRY.get(view_name):
                collection.add(view_cls, lambda: view_cls(create_engine(db_url)))  # pylint: disable=cell-var-from-loop
            else:
                raise ValueError(
                    f"View {view_name} not supported. "
                    f"Available views: {list(STRUCTURED_VIEWS_REGISTRY) + list(FREEFORM_VIEWS_REGISTRY)}."
                )

        return collection

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        db_url = None
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
                prediction = ExecutionResult(exception=exc)
            except Text2SQLError as exc:
                prediction = ExecutionResult(exception=exc)
            else:
                prediction = ExecutionResult(
                    iql=result.context.get("iql", None),
                    sql=result.context.get("sql", None),
                )
                used_view = self.collection.get(result.view_name)
                db_url = (
                    used_view._sqlalchemy_engine.url
                    if isinstance(used_view, SqlAlchemyBaseView)
                    else used_view._engine.url
                )

            reference = ExecutionResult(
                iql=data["iql"],
                sql=data["sql"],
            )
            result = EvaluationResult(
                question=data["question"],
                reference=reference,
                prediction=prediction,
                db_url=db_url,
            )
            results.append(result)

        return results
