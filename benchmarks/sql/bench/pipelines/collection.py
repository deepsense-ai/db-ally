from typing import Any, Dict

import dbally
from dbally.collection.collection import Collection
from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.view_selection.llm_view_selector import LLMViewSelector

from ..views import VIEWS_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult


class CollectionEvaluationPipeline(EvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating collection predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.collection = self.get_collection(config.setup)

    def get_collection(self, config: Dict) -> Collection:
        """
        Sets up the collection based on the configuration.

        Args:
            config: The collection configuration.

        Returns:
            The collection.
        """
        generator_llm = self.get_llm(config.generator_llm)
        selector_llm = self.get_llm(config.selector_llm)
        view_selector = LLMViewSelector(selector_llm)

        collection = dbally.create_collection(
            name=config.name,
            llm=generator_llm,
            view_selector=view_selector,
        )
        collection.n_retries = 0

        for view_name in config.views:
            view_cls = VIEWS_REGISTRY[view_name]
            collection.add(view_cls, lambda: view_cls(self.db))  # pylint: disable=cell-var-from-loop

        if config.fallback:
            fallback = dbally.create_collection(
                name=config.fallback,
                llm=generator_llm,
                view_selector=view_selector,
            )
            fallback.n_retries = 0
            fallback_cls = VIEWS_REGISTRY[config.fallback]
            fallback.add(fallback_cls, lambda: fallback_cls(self.db))
            collection.set_fallback(fallback)

        return collection

    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the collection evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
        try:
            result = await self.collection.ask(
                question=data["question"],
                dry_run=True,
                return_natural_response=False,
            )
        # TODO: Refactor exception handling for IQLError for filters and aggregation
        except IQLError as exc:
            prediction = ExecutionResult(
                iql=IQLResult(filters=exc.source),
                exception=exc,
            )
        # TODO: Remove this broad exception handling once the Text2SQL view is fixed
        except (UnsupportedQueryError, Exception) as exc:  # pylint: disable=broad-except
            prediction = ExecutionResult(exception=exc)
        else:
            iql = IQLResult(filters=result.context["iql"]) if "iql" in result.context else None
            prediction = ExecutionResult(
                view=result.view_name,
                iql=iql,
                sql=result.context.get("sql"),
            )

        reference = ExecutionResult(
            view=data["view"],
            iql=IQLResult(
                filters=data["iql_filters"],
                aggregation=data["iql_aggregation"],
            ),
            sql=data["sql"],
        )
        return EvaluationResult(
            question=data["question"],
            reference=reference,
            prediction=prediction,
        )
