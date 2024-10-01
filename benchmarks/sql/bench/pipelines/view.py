# pylint: disable=duplicate-code

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Dict, Type

from dbally.llms.base import LLM
from dbally.views.exceptions import ViewExecutionError
from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import VIEWS_REGISTRY
from .base import IQL, EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult, ViewEvaluationMixin, ViewT


class ViewEvaluationPipeline(EvaluationPipeline, ViewEvaluationMixin[ViewT], ABC):
    """
    View evaluation pipeline.
    """

    @cached_property
    def llm(self) -> LLM:
        """
        Returns the LLM based on the configuration.
        """
        return self._get_llm(self.config.setup.llm)

    @cached_property
    @abstractmethod
    def views(self) -> Dict[str, Type[ViewT]]:
        """
        Returns the view classes mapping based on the configuration
        """


class IQLViewEvaluationPipeline(ViewEvaluationPipeline[SqlAlchemyBaseView]):
    """
    IQL view evaluation pipeline.
    """

    @cached_property
    def views(self) -> Dict[str, Type[SqlAlchemyBaseView]]:
        """
        Returns the view classes mapping based on the configuration.
        """
        return {
            view: cls
            for views in self.config.setup.views.values()
            for view in views
            if issubclass(cls := VIEWS_REGISTRY[view], SqlAlchemyBaseView)
        }

    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
        view = self.views[data["view_name"]](self.dbs[data["db_id"]])

        try:
            result = await view.ask(
                query=data["question"],
                llm=self.llm,
                contexts=self.contexts,
                dry_run=True,
                n_retries=0,
            )
        except ViewExecutionError as exc:
            prediction = ExecutionResult(
                view_name=data["view_name"],
                iql=IQLResult(
                    filters=IQL.from_query(exc.iql.filters),
                    aggregation=IQL.from_query(exc.iql.aggregation),
                ),
            )
        else:
            prediction = ExecutionResult(
                view_name=data["view_name"],
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
                ),
                aggregation=IQL(
                    source=data["iql_aggregation"],
                    unsupported=data["iql_aggregation_unsupported"],
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


class SQLViewEvaluationPipeline(ViewEvaluationPipeline[BaseText2SQLView]):
    """
    SQL view evaluation pipeline.
    """

    @cached_property
    def views(self) -> Dict[str, Type[BaseText2SQLView]]:
        """
        Returns the view classes mapping based on the configuration.
        """
        return {
            db: cls
            for db, view in self.config.setup.views.items()
            if issubclass(cls := VIEWS_REGISTRY[view], BaseText2SQLView)
        }

    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
        view = self.views[data["db_id"]](self.dbs[data["db_id"]])

        try:
            result = await view.ask(
                query=data["question"],
                llm=self.llm,
                dry_run=True,
                n_retries=0,
            )
        # TODO: Remove this broad exception handling once the Text2SQL view is fixed
        except Exception:  # pylint: disable=broad-except
            prediction = ExecutionResult(
                view_name=view.__class__.__name__,
            )
        else:
            prediction = ExecutionResult(
                view_name=view.__class__.__name__,
                sql=result.metadata["sql"],
            )

        reference = ExecutionResult(
            view_name=data["view_name"],
            sql=data["sql"],
        )

        return EvaluationResult(
            db_id=data["db_id"],
            question_id=data["question_id"],
            question=data["question"],
            reference=reference,
            prediction=prediction,
        )
