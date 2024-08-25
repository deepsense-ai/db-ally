# pylint: disable=duplicate-code

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from sqlalchemy import create_engine

from dbally.views.exceptions import ViewExecutionError
from dbally.views.freeform.text2sql.view import BaseText2SQLView
from dbally.views.sqlalchemy_base import SqlAlchemyBaseView

from ..views import VIEWS_REGISTRY
from .base import IQL, EvaluationPipeline, EvaluationResult, ExecutionResult, IQLResult


class ViewEvaluationPipeline(EvaluationPipeline, ABC):
    """
    View evaluation pipeline.
    """

    def __init__(self, config: Dict) -> None:
        """
        Constructs the pipeline for evaluating IQL predictions.

        Args:
            config: The configuration for the pipeline.
        """
        self.llm = self.get_llm(config.setup.llm)
        self.dbs = self.get_dbs(config.setup)
        self.views = self.get_views(config.setup)

    def get_dbs(self, config: Dict) -> Dict:
        """
        Returns the database object based on the database name.

        Args:
            config: The database configuration.

        Returns:
            The database object.
        """
        return {db: create_engine(f"sqlite:///data/{db}.db") for db in config.views}

    @abstractmethod
    def get_views(self, config: Dict) -> Dict[str, Type[SqlAlchemyBaseView]]:
        """
        Creates the view classes mapping based on the configuration.

        Args:
            config: The views configuration.

        Returns:
            The view classes mapping.
        """


class IQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    IQL view evaluation pipeline.
    """

    def get_views(self, config: Dict) -> Dict[str, Type[SqlAlchemyBaseView]]:
        """
        Creates the view classes mapping based on the configuration.

        Args:
            config: The views configuration.

        Returns:
            The view classes mapping.
        """
        return {
            view_name: VIEWS_REGISTRY[view_name] for view_names in config.views.values() for view_name in view_names
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
                dry_run=True,
                n_retries=0,
            )
        except ViewExecutionError as exc:
            prediction = ExecutionResult(
                view_name=data["view_name"],
                iql=IQLResult(
                    filters=IQL.from_generator_state(exc.iql.filters),
                    aggregation=IQL.from_generator_state(exc.iql.aggregation),
                ),
            )
        else:
            prediction = ExecutionResult(
                view_name=data["view_name"],
                iql=IQLResult(
                    filters=IQL(
                        source=result.context["iql"],
                        unsupported=False,
                        valid=True,
                    ),
                    aggregation=IQL(
                        source=None,
                        unsupported=False,
                        valid=True,
                    ),
                ),
                sql=result.context["sql"],
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


class SQLViewEvaluationPipeline(ViewEvaluationPipeline):
    """
    SQL view evaluation pipeline.
    """

    def get_views(self, config: Dict) -> Dict[str, Type[BaseText2SQLView]]:
        """
        Creates the view classes mapping based on the configuration.

        Args:
            config: The views configuration.

        Returns:
            The view classes mapping.
        """
        return {db_id: VIEWS_REGISTRY[view_name] for db_id, view_name in config.views.items()}

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
                sql=result.context["sql"],
            )

        reference = ExecutionResult(
            view_name=data["view_name"],
            sql=data["sql"],
        )

        return EvaluationResult(
            db_id=data["db_id"],
            question=data["question"],
            reference=reference,
            prediction=prediction,
        )
