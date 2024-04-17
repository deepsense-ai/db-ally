import abc
from typing import List

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.iql import IQLError, IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.llm_client.base import LLMClient
from dbally.views.exposed_functions import ExposedFunction

from .base import BaseView


class BaseStructuredView(BaseView):
    """
    Base class for all structured [Views](../../concepts/views.md). All classes implementing this interface has\
    to be able to list all available filters, apply them and execute queries.
    """

    def get_iql_generator(self, llm_client: LLMClient) -> IQLGenerator:
        """
        Returns the IQL generator for the view.

        Args:
            llm_client: LLM client used to generate the IQL queries

        Returns:
            IQLGenerator: IQL generator for the view
        """
        return IQLGenerator(llm_client=llm_client)

    async def ask(
        self, query: str, llm_client: LLMClient, event_tracker: EventTracker, n_retries: int = 3, dry_run: bool = False
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result. It generates the IQL query from the natural language query\
        and applies the filters to the view. It retries the process in case of errors.

        Args:
            query: The natural language query to execute.
            llm_client: The LLM client used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.

        Returns:
            The result of the query.
        """
        iql_generator = self.get_iql_generator(llm_client)
        filter_list = self.list_filters()

        iql_filters, conversation = await iql_generator.generate_iql(
            question=query, filters=filter_list, event_tracker=event_tracker
        )

        for _ in range(n_retries):
            try:
                filters = await IQLQuery.parse(iql_filters, filter_list)
                await self.apply_filters(filters)
                break
            except (IQLError, ValueError) as e:
                conversation = iql_generator.add_error_msg(conversation, [e])
                iql_filters, conversation = await iql_generator.generate_iql(
                    question=query,
                    filters=filter_list,
                    event_tracker=event_tracker,
                    conversation=conversation,
                )
                continue

        result = self.execute(dry_run=dry_run)
        result.context["iql"] = iql_filters

        return result

    @abc.abstractmethod
    def list_filters(self) -> List[ExposedFunction]:
        """

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
