from typing import Dict, List

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import STRUCTURED_VIEW_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult


class IQLEvaluationPipeline(EvaluationPipeline):
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
        self.view = self.get_view(config.data.views)

    def get_view(self, config: Dict) -> SqlAlchemyBaseView:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.

        Raises:
            ValueError: If the view name is not supported.
        """
        if not config.structured:
            raise ValueError("No structured views found in the configuration.")

        view_name, db_url = list(config.structured.items())[0]
        if view_cls := STRUCTURED_VIEW_REGISTRY.get(view_name):
            return view_cls(create_engine(db_url))

        raise ValueError(f"View {view_name} not supported. Available views: {STRUCTURED_VIEW_REGISTRY}.")

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        results = []

        for data in tqdm(dataset, desc="IQL evaluation"):
            try:
                result = await self.view.ask(
                    query=data["question"],
                    llm=self.llm,
                    n_retries=0,
                    dry_run=True,
                )
            except (IQLError, UnsupportedQueryError) as exc:
                query = "UNSUPPORTED_QUERY" if isinstance(exc, UnsupportedQueryError) else exc.source
                prediction = ExecutionResult(iql=query, exception=exc)
            else:
                prediction = ExecutionResult(
                    iql=result.context.get("iql", None),
                    sql=result.context.get("sql", None),
                )
            reference = ExecutionResult(
                iql=data["iql"],
                sql=data["sql"],
            )
            results.append(
                EvaluationResult(
                    db_url=self.view._sqlalchemy_engine.url,
                    question=data["question"],
                    reference=reference,
                    prediction=prediction,
                ),
            )

        return results
