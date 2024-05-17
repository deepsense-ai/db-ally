import abc
from typing import List, Optional

from dbally.audit.event_tracker import EventTracker
from dbally.data_models.execution_result import ViewExecutionResult
from dbally.llm_client.base import LLMClient, LLMOptions
from dbally.similarity import AbstractSimilarityIndex


class BaseView(metaclass=abc.ABCMeta):
    """
    Base class for all [Views](../../concepts/views.md), which are the main building blocks of db-ally. All classes\
    implementing this interface have to be able to execute queries and return the result.
    """

    @abc.abstractmethod
    async def ask(
        self,
        query: str,
        llm_client: LLMClient,
        event_tracker: EventTracker,
        n_retries: int = 3,
        dry_run: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ViewExecutionResult:
        """
        Executes the query and returns the result.

        Args:
            query: The natural language query to execute.
            llm_client: The LLM client used to execute the query.
            event_tracker: The event tracker used to audit the query execution.
            n_retries: The number of retries to execute the query in case of errors.
            dry_run: If True, the query will not be used to fetch data from the datasource.
            llm_options: options to use for the LLM client.

        Returns:
            The result of the query.
        """

    def list_similarity_indexes(self) -> List[AbstractSimilarityIndex]:
        """
        Lists all the similarity indexes used by the view.

        Returns:
            List of similarity indexes.
        """
        return []
