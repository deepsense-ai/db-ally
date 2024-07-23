from abc import ABC
from typing import Any, Dict, Type

from dbally.iql._exceptions import IQLError
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import VIEWS_REGISTRY
from .base import EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult


class ViewEvaluationPipeline(EvaluationPipeline, ABC):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.llm = self.get_llm(config.setup.llm)


class IQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.views = self.get_views(config.setup)

    def get_views(self, config: Dict) -> Dict[str, Type[SqlAlchemyBaseView]]:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.
        """
        return {view: VIEWS_REGISTRY[view] for view in config.views}

    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
        view = self.views[data["view"]](self.db)
        try:
            result = await view.ask(
                query=data["question"],
                llm=self.llm,
                dry_run=True,
                n_retries=0,
            )
        # TODO: Refactor exception handling for IQLError for filters and aggregation
        except IQLError as exc:
            prediction = ExecutionResult(
                view=data["view"],
                iql=IQLResult(filters=exc.source),
                exception=exc,
            )
        except (UnsupportedQueryError, Exception) as exc:  # pylint: disable=broad-except
            prediction = ExecutionResult(
                view=data["view"],
                exception=exc,
            )
        else:
            prediction = ExecutionResult(
                view=data["view"],
                iql=IQLResult(filters=result.context["iql"]),
                sql=result.context["sql"],
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


class SQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    Collection evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        super().__init__(config)
        self.view = self.get_view(config.setup)

    def get_view(self, config: Dict) -> Type[BaseText2SQLView]:
        """
        Returns the view object based on the view name.

        Args:
            config: The view configuration.

        Returns:
            The view object.
        """
        return VIEWS_REGISTRY[config.view]

    async def __call__(self, data: Dict[str, Any]) -> EvaluationResult:
        """
        Runs the evaluation pipeline.

        Args:
            data: The evaluation data.

        Returns:
            The evaluation result.
        """
        view = self.view(self.db)
        try:
            result = await view.ask(
                query=data["question"],
                llm=self.llm,
                dry_run=True,
                n_retries=0,
            )
        # TODO: Remove this broad exception handling once the Text2SQL view is fixed
        except Exception as exc:  # pylint: disable=broad-except
            prediction = ExecutionResult(
                view=self.view.__name__,
                exception=exc,
            )
        else:
            prediction = ExecutionResult(
                view=self.view.__name__,
                sql=result.context["sql"],
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
