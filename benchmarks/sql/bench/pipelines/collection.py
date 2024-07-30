from typing import Any, Dict

from sqlalchemy import create_engine

import dbally
from dbally.collection.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.view_selection.llm_view_selector import LLMViewSelector
from dbally.views.structured import IQLGenerationError

from ..views import VIEWS_REGISTRY
from .base import IQL, EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult


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
                dry_run=True,
                return_natural_response=False,
            )
        except NoViewFoundError:
            prediction = ExecutionResult(
                view_name=None,
                iql=None,
                sql=None,
            )
        except IQLGenerationError as exc:
            prediction = ExecutionResult(
                view_name=exc.view_name,
                iql=IQLResult(
                    filters=IQL(
                        source=exc.filters,
                        unsupported=isinstance(exc.__cause__, UnsupportedQueryError),
                        valid=not (exc.filters and not exc.aggregation and isinstance(exc.__cause__, IQLError)),
                    ),
                    aggregation=IQL(
                        source=exc.aggregation,
                        unsupported=isinstance(exc.__cause__, UnsupportedQueryError),
                        valid=not (exc.aggregation and isinstance(exc.__cause__, IQLError)),
                    ),
                ),
                sql=None,
            )
        else:
            prediction = ExecutionResult(
                view_name=result.view_name,
                iql=IQLResult(
                    filters=IQL(
                        source=result.context.get("iql"),
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql=result.context.get("sql"),
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
            question=data["question"],
            reference=reference,
            prediction=prediction,
        )
