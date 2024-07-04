import abc
from collections import defaultdict
from typing import Dict, List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.iql import IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.views.exposed_functions import ExposedFunction

from ..similarity import AbstractSimilarityIndex
from .base import BaseView, IndexLocation


class BaseStructuredView(BaseView):
    """
    Base class for all structured [Views](../../concepts/views.md). All classes implementing this interface has\
    to be able to list all available filters, apply them and execute queries.
    """

    def get_iql_generator(self, llm: LLM) -> IQLGenerator:
        """
        Returns the IQL generator for the view.

        Args:
            llm: LLM used to generate the IQL queries.

        Returns:
            IQL generator for the view.
        """
        return IQLGenerator(llm=llm)

    async def ask(
        self,
        query: str,
        llm: LLM,
        event_tracker: EventTracker,
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
        """
        iql_generator = self.get_iql_generator(llm)

        filters = self.list_filters()
        examples = self.list_few_shots()

        iql = await iql_generator.generate_iql(
            question=query,
            filters=filters,
            examples=examples,
            event_tracker=event_tracker,
            llm_options=llm_options,
            n_retries=n_retries,
        )
        await self.apply_filters(iql)

        result = self.execute(dry_run=dry_run)
        result.context["iql"] = f"{iql}"

        return result

    @abc.abstractmethod
    def list_filters(self) -> List[ExposedFunction]:
        """
        Lists all available filters for the View.

        Returns:
            Filters defined inside the View.
        """

    @abc.abstractmethod
    async def apply_filters(self, filters: IQLQuery) -> None:
        """
        Applies the chosen filters to the view.

        Args:
            filters: [IQLQuery](../../concepts/iql.md) object representing the filters to apply
        """

    @abc.abstractmethod
    def execute(self, dry_run: bool = False) -> ViewExecutionResult:
        """
        Executes the query and returns the result.

        Args:
            dry_run: if True, should only generate the query without executing it
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
