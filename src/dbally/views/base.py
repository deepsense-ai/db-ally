import abc

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.llm_client.base import LLMClient


class BaseView(metaclass=abc.ABCMeta):
    """
    Base class for all [Views](../../concepts/views.md), which are the main building blocks of db-ally. All classes\
    implementing this interface have to be able to execute queries and return the result.
    """

    # TODO LLMOptions must be passed here too.
    @abc.abstractmethod
    async def ask(
        self, query: str, llm_client: LLMClient, event_tracker: EventTracker, n_retries: int = 3, dry_run: bool = False
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result.

        Args:
            query: The natural language query to execute.
            llm_client: The LLM client used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.

        Returns:
            The result of the query.
        """
