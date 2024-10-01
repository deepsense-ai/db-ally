from functools import cached_property
from typing import Any, Dict, Type, Union

import dbally
from dbally.collection.collection import Collection
from dbally.collection.exceptions import NoViewFoundError
from dbally.llms.base import LLM
from dbally.view_selection.llm_view_selector import LLMViewSelector
from dbally.views.exceptions import ViewExecutionError
from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import VIEWS_REGISTRY
from .base import IQL, EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult, ViewEvaluationMixin


class CollectionEvaluationPipeline(
    EvaluationPipeline, ViewEvaluationMixin[Union[SqlAlchemyBaseView, BaseText2SQLView]]
):
    """
    Collection evaluation pipeline.
    """

    @cached_property
    def selector(self) -> LLM:
        """
        Returns the selector LLM.
        """
        return self._get_llm(self.config.setup.selector_llm)

    @cached_property
    def generator(self) -> LLM:
        """
        Returns the generator LLM.
        """
        return self._get_llm(self.config.setup.generator_llm)

    @cached_property
    def views(self) -> Dict[str, Type[Union[SqlAlchemyBaseView, BaseText2SQLView]]]:
        """
        Returns the view classes mapping based on the configuration.
        """
        return {
            db: cls
            for db, views in self.config.setup.views.items()
            for view in views
            if issubclass(cls := VIEWS_REGISTRY[view], (SqlAlchemyBaseView, BaseText2SQLView))
        }

    @cached_property
    def collection(self) -> Collection:
        """
        Returns the collection used for evaluation.
        """
        view_selector = LLMViewSelector(self.selector)

        collection = dbally.create_collection(
            name=self.config.setup.name,
            llm=self.generator,
            view_selector=view_selector,
        )
        collection.n_retries = 0

        for db, view in self.views.items():
            collection.add(view, lambda: view(self.dbs[db]))  # pylint: disable=cell-var-from-loop

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
