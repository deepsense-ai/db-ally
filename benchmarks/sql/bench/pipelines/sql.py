from typing import Dict, List

from datasets import Dataset
from sqlalchemy import create_engine
from tqdm import tqdm

from dbally.views.freeform.text2sql.view import BaseText2SQLView

from ..views import FREEFORM_VIEW_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult


class SQLEvaluationPipeline(EvaluationPipeline):
    """
    Pipeline for evaluating SQL predictions.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating SQL predictions.

        Args:
            config: The configuration for the pipeline.

        Raises:
            ValueError: If the view name is not supported.
        """
        self.view = self.get_view(config.data.views)
        self.llm = self.get_llm(config.llm)

    def get_view(self, config: Dict) -> BaseText2SQLView:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.

        Raises:
            ValueError: If the view name is not supported
        """
        if not config.freeform:
            raise ValueError("No freeform views found in the configuration.")

        view_name, db_url = list(config.freeform.items())[0]
        if view_cls := FREEFORM_VIEW_REGISTRY.get(view_name):
            return view_cls(create_engine(db_url))

        raise ValueError(f"View {view_name} not supported. Available views: {FREEFORM_VIEW_REGISTRY}.")

    async def __call__(self, dataset: Dataset) -> List[EvaluationResult]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        results = []

        for data in tqdm(dataset, desc="SQL evaluation"):
            result = await self.view.ask(
                query=data["question"],
                llm=self.llm,
                n_retries=0,
                dry_run=True,
            )
            prediction = ExecutionResult(sql=result.context["sql"])
            reference = ExecutionResult(
                iql=result.context.get("iql", None),
                sql=result.context.get("sql", None),
            )
            results.append(
                EvaluationResult(
                    db_url=self.view._engine.url,
                    question=data["question"],
                    reference=reference,
                    prediction=prediction,
                ),
            )

        return results
