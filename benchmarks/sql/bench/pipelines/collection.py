from typing import Any, Dict

from omegaconf import DictConfig
from sqlalchemy import create_engine

import dbally
from dbally.collection.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.view_selection.llm_view_selector import LLMViewSelector
from dbally.views.exceptions import ViewExecutionError

from ..views import VIEWS_REGISTRY
from .base import IQL, EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult


class CollectionEvaluationPipeline(EvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: DictConfig) -> None:
        """
        Constructs the pipeline for evaluating collection predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.collection = self.get_collection(config.setup)

    def get_collection(self, config: DictConfig) -> Collection:
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

        for db_name, view_names in config.views.items():
            db = create_engine(f"sqlite:///data/{db_name}.db")
            for view_name in view_names:
                view_cls = VIEWS_REGISTRY[view_name]
                collection.add(view_cls, lambda: view_cls(db))  # pylint: disable=cell-var-from-loop

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
                contexts=self.contexts,
                dry_run=True,
                return_natural_response=False,
            )
        except NoViewFoundError:
            prediction = ExecutionResult()
        except ViewExecutionError as exc:
            prediction = ExecutionResult(
                view_name=exc.view_name,
                iql=IQLResult(
                    filters=IQL.from_query(exc.iql.filters),
                    aggregation=IQL.from_query(exc.iql.aggregation),
                ),
            )
        else:
            prediction = ExecutionResult(
                view_name=result.view_name,
                iql=IQLResult(
                    filters=IQL(source=result.metadata["iql"]["filters"]),
                    aggregation=IQL(source=result.metadata["iql"]["aggregation"]),
                ),
                sql=result.metadata["sql"],
            )

        reference = ExecutionResult(
            view_name=data["view_name"],
            iql=IQLResult(
                filters=IQL(
                    source=data["iql_filters"],
                    unsupported=data["iql_filters_unsupported"],
                    valid=True,
                ),
                aggregation=IQL(
                    source=data["iql_aggregation"],
                    unsupported=data["iql_aggregation_unsupported"],
                    valid=True,
                ),
                context=data["iql_context"],
            ),
            sql=data["sql"],
        )

        return EvaluationResult(
            db_id=data["db_id"],
            question_id=data["question_id"],
            question=data["question"],
            reference=reference,
            prediction=prediction,
        )
