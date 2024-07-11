from dataclasses import asdict
from typing import Dict, List, Tuple

from constants import VIEW_REGISTRY, ViewName
from datasets import Dataset
from iql.metrics import (
    calculate_exact_match,
    calculate_hallucinated_filters,
    calculate_invalid_iql,
    calculate_unsupported_iql,
    calculate_valid_iql,
)
from results import TextToIQLResult
from sqlalchemy import create_engine

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView


class TextToIQLEvaluationPipeline:
    """
    Pipeline for evaluating IQL predictions.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the.

        Raises:
            ValueError: If the view name is not supported.
        """
        self.engine = create_engine(config.db_url)
        self.view = self.get_view(config.view_name)
        self.iql_generator = self.get_iql_generator(config.llm)

    def get_view(self, view_name: str) -> SqlAlchemyBaseView:
        """
        Returns the view object based on the view name.

        Args:
            view_name: The name of the view.

        Returns:
            The view object.

        Raises:
            ValueError: If the view name is not supported
        """
        allowed_views = [view.value for view in ViewName]
        if view_name not in allowed_views:
            raise ValueError(f"View {view_name} not supported. Available views: {allowed_views}")
        return VIEW_REGISTRY[ViewName(view_name)](self.engine)

    def get_iql_generator(self, llm_config: Dict) -> IQLGenerator:
        """
        Returns the IQL generator based on the LLM configuration.

        Args:
            llm_config: The LLM configuration.

        Returns:
            The IQL generator.
        """
        if llm_config.model_name.startswith("local/"):
            llm = LocalLLM(
                model_name=llm_config.model_name.split("/", 1)[1],
                api_key=llm_config.api_key,
            )
        else:
            llm = LiteLLM(
                model_name=llm_config.model_name,
                api_key=llm_config.api_key,
            )
        return IQLGenerator(llm)

    async def compute_metrics(self, results: List[TextToIQLResult]) -> Dict[str, float]:
        """
        Computes the metrics for IQL predictions.

        Args:
            results: The list of IQL predictions.

        Returns:
            The metrics for the IQL predictions.
        """
        filters = self.view.list_filters()

        return {
            "exact_match": calculate_exact_match(results),
            "valid_iql": await calculate_valid_iql(results, filters),
            "invalid_iql": await calculate_invalid_iql(results, filters),
            "unsupported_iql": calculate_unsupported_iql(results),
            "hallucinated_iql": calculate_hallucinated_filters(results, filters),
        }

    async def __call__(self, dataset: Dataset) -> Tuple[Dict[str, float], List[Dict[str, str]]]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        filters = self.view.list_filters()
        examples = self.view.list_few_shots()
        results = []

        for data in dataset:
            try:
                predicted_iql = await self.iql_generator.generate_iql(
                    question=data["question"],
                    filters=filters,
                    examples=examples,
                    n_retries=0,
                )
            except UnsupportedQueryError:
                result = "UNSUPPORTED_QUERY"
            except IQLError as exc:
                result = exc.source
            else:
                result = str(predicted_iql)

            results.append(
                TextToIQLResult(question=data["question"], ground_truth_iql=data["iql"], predicted_iql=result)
            )

        metrics = await self.compute_metrics(results)
        results = [asdict(result) for result in results]

        return metrics, results
