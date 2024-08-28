import abc
from collections import defaultdict
from typing import Dict, List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.iql._query import IQLAggregationQuery, IQLFiltersQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.views.exceptions import ViewExecutionError
from dbally.views.exposed_functions import ExposedFunction

from ..similarity import AbstractSimilarityIndex
from .base import BaseView, IndexLocation


class BaseStructuredView(BaseView):
    """
    Base class for all structured [Views](../../concepts/views.md). All classes implementing this interface has\
    to be able to list all available filters, apply them and execute queries.
    """

    def get_iql_generator(self) -> IQLGenerator:
        """
        Returns the IQL generator for the view.

        Returns:
            IQL generator for the view.
        """
        return IQLGenerator()

    async def ask(
        self,
        query: str,
        llm: LLM,
        event_tracker: Optional[EventTracker] = None,
        n_retries: int = 3,
        dry_run: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result. It generates the IQL query from the natural language query\
        and applies the filters to the view. It retries the process in case of errors.

        Args:
            query: The natural language query to execute.
            llm: The LLM used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.
            llm_options: Options to use for the LLM.

        Returns:
            The result of the query.

        Raises:
            ViewExecutionError: When an error occurs while executing the view.
        """
        filters = self.list_filters()
        examples = self.list_few_shots()
        aggregations = self.list_aggregations()

        iql_generator = self.get_iql_generator()
        iql = await iql_generator(
            question=query,
            filters=filters,
            aggregations=aggregations,
            examples=examples,
            llm=llm,
            event_tracker=event_tracker,
            llm_options=llm_options,
            n_retries=n_retries,
        )

        if iql.failed:
            raise ViewExecutionError(
                view_name=self.__class__.__name__,
                iql=iql,
            )

        if iql.filters:
            await self.apply_filters(iql.filters)

        if iql.aggregation:
            await self.apply_aggregation(iql.aggregation)

        result = self.execute(dry_run=dry_run)
        result.context["iql"] = {
            "filters": str(iql.filters) if iql.filters else None,
            "aggregation": str(iql.aggregation) if iql.aggregation else None,
        }
        return result

    @abc.abstractmethod
    def list_filters(self) -> List[ExposedFunction]:
        """
        Lists all available filters for the View.

        Returns:
            Filters defined inside the View.
        """

    @abc.abstractmethod
    def list_aggregations(self) -> List[ExposedFunction]:
        """
        Lists all available aggregations for the View.

        Returns:
            Aggregations defined inside the View.
        """

    @abc.abstractmethod
    async def apply_filters(self, filters: IQLFiltersQuery) -> None:
        """
        Applies the chosen filters to the view.

        Args:
            filters: IQLQuery object representing the filters to apply.
        """

    @abc.abstractmethod
    async def apply_aggregation(self, aggregation: IQLAggregationQuery) -> None:
        """
        Applies the chosen aggregation to the view.

        Args:
            aggregation: IQLQuery object representing the aggregation to apply.
        """

    @abc.abstractmethod
    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        """
        Executes the query and returns the result.

        Args:
            dry_run: if True, should only generate the query without executing it.

        Returns:
            The view execution result.
        """

    def list_similarity_indexes(self) -> Dict[AbstractSimilarityIndex, List[IndexLocation]]:
        """
        Lists all the similarity indexes used by the view.

        Returns:
            Mapping of similarity indexes to their locations in the (view_name, filter_name, argument_name) format.
        """
        indexes = defaultdict(list)
        filters = self.list_filters()
        for filter_ in filters:
            for param in filter_.parameters:
                if param.similarity_index:
                    indexes[param.similarity_index].append((self.__class__.__name__, filter_.name, param.name))
        return indexes
