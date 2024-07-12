import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Dict, List, Tuple

from datasets import Dataset
from iql.metrics import calculate_exact_match as calculate_iql_exact_match
from iql.metrics import (
    calculate_hallucinated_filters,
    calculate_invalid_iql,
    calculate_unsupported_iql,
    calculate_valid_iql,
)
from results import TextToIQLResult, TextToSQLResult
from sqlalchemy import create_engine, text
from text2sql.metrics import calculate_exact_match as calculate_sql_exact_match
from text2sql.metrics import calculate_exec_acc, calculate_undefined_error_ratio, calculate_valid_sql, calculate_ves
from views import FREEFORM_VIEW_REGISTRY, STRUCTURED_VIEW_REGISTRY

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.litellm import LiteLLM
from dbally.llms.local import LocalLLM
from dbally.views.freeform.text2sql.prompt import SQL_GENERATION_TEMPLATE, SQLGenerationPromptFormat
from dbally.views.freeform.text2sql.view import BaseText2SQLView, SQLParameterOption
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

Metrics = Dict[str, float]
Results = List[Dict[str, str]]


class EvaluationPipeline(ABC):
    """
    Evaluation pipeline base class.
    """

    def __init__(self, config: Dict) -> None:
        self.engine = create_engine(config.db_url)

    def get_llm(self, llm_config: Dict) -> LLM:
        """
        Returns the LLM based on the configuration.

        Args:
            llm_config: The LLM configuration.

        Returns:
            The LLM object.
        """
        if llm_config.model_name.startswith("local/"):
            return LocalLLM(llm_config.model_name.split("/", 1)[1])
        return LiteLLM(llm_config.model_name)

    @abstractmethod
    async def __call__(self, dataset: Dataset) -> Tuple[Metrics, Results]:
        """
        Runs the evaluation pipeline.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """


class TextToIQLEvaluationPipeline(EvaluationPipeline):
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
        super().__init__(config)
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
        if view_name not in STRUCTURED_VIEW_REGISTRY:
            raise ValueError(f"View {view_name} not supported. Available views: {STRUCTURED_VIEW_REGISTRY}.")
        return STRUCTURED_VIEW_REGISTRY[view_name](self.engine)

    def get_iql_generator(self, llm_config: Dict) -> IQLGenerator:
        """
        Returns the IQL generator based on the LLM configuration.

        Args:
            llm_config: The LLM configuration.

        Returns:
            The IQL generator.
        """
        llm = self.get_llm(llm_config)
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
            "exact_match": calculate_iql_exact_match(results),
            "valid_iql": await calculate_valid_iql(results, filters),
            "invalid_iql": await calculate_invalid_iql(results, filters),
            "unsupported_iql": calculate_unsupported_iql(results),
            "hallucinated_iql": calculate_hallucinated_filters(results, filters),
        }

    async def __call__(self, dataset: Dataset) -> Tuple[Metrics, Results]:
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


class TextToSQLEvaluationPipeline(EvaluationPipeline):
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
        super().__init__(config)
        self.view = self.get_view(config.view_name)
        self.sql_generator = self.get_sql_generator(config.llm)

    def get_view(self, view_name: str) -> BaseText2SQLView:
        """
        Returns the view object based on the view name.

        Args:
            view_name: The name of the view.

        Returns:
            The view object.

        Raises:
            ValueError: If the view name is not supported
        """
        if view_name not in FREEFORM_VIEW_REGISTRY:
            raise ValueError(f"View {view_name} not supported. Available views: {FREEFORM_VIEW_REGISTRY}.")
        return FREEFORM_VIEW_REGISTRY[view_name](self.engine)

    def get_sql_generator(self, llm_config: Dict) -> LLM:
        """
        Returns the IQL generator based on the LLM configuration.

        Args:
            llm_config: The LLM configuration.

        Returns:
            The IQL generator.
        """
        # TODO: Implement SQL generator
        return self.get_llm(llm_config)

    async def compute_metrics(self, results: List[TextToSQLResult]) -> Dict[str, float]:
        """
        Computes the metrics for IQL predictions.

        Args:
            results: The list of IQL predictions.

        Returns:
            The metrics for the IQL predictions.
        """
        return {
            "valid_sql": calculate_valid_sql(results, self.engine),
            "undefined_error": calculate_undefined_error_ratio(results),
            "exact_match": calculate_sql_exact_match(results),
            "execution_accuracy": calculate_exec_acc(results, self.engine),
            "valid_efficiency_score": calculate_ves(results, self.engine),
        }

    async def __call__(self, dataset: Dataset) -> Tuple[Metrics, Results]:
        """
        Runs the pipeline for evaluating IQL predictions.

        Args:
            dataset: The dataset containing the questions and ground truth IQL queries.

        Returns:
            The list of IQL predictions.
        """
        tables = self.view.get_tables()
        examples = self.view.list_few_shots()
        results = []

        for data in dataset:
            try:
                # TODO: Refactor this once the SQL generator is implemented
                prompt_format = SQLGenerationPromptFormat(
                    question=data["question"],
                    dialect=self.engine.dialect.name,
                    tables=tables,
                    examples=examples,
                )
                formatted_prompt = SQL_GENERATION_TEMPLATE.format_prompt(prompt_format)
                response = await self.sql_generator.generate_text(formatted_prompt)
                response = json.loads(response)
                params = [SQLParameterOption.from_dict(param) for param in response.get("parameters", [])]
                params = {param.name: param.value for param in params}
                stmt = text(response.get("sql", ""))
                stmt = stmt.bindparams(**params)
                result = str(stmt.compile(compile_kwargs={"literal_binds": True}))
            except Exception:  # pylint: disable=broad-except
                result = ""

            results.append(
                TextToSQLResult(question=data["question"], ground_truth_sql=data["sql"], predicted_sql=result)
            )

        metrics = await self.compute_metrics(results)
        results = [asdict(result) for result in results]

        return metrics, results
