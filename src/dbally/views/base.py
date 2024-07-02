import abc
from typing import Dict, List, Optional, Tuple

from dbally.audit.event_tracker import EventTracker
from dbally.collection.results import ViewExecutionResult
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.prompt.elements import FewShotExample
from dbally.similarity import AbstractSimilarityIndex

IndexLocation = Tuple[str, str, str]


class BaseView(metaclass=abc.ABCMeta):
    """
    Base class for all [Views](../../concepts/views.md), which are the main building blocks of db-ally. All classes\
    implementing this interface have to be able to execute queries and return the result.
    """

    @abc.abstractmethod
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
        Executes the query and returns the result.

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

    def list_similarity_indexes(self) -> Dict[AbstractSimilarityIndex, List[IndexLocation]]:
        """
        Lists all the similarity indexes used by the view.

        Returns:
            Mapping of similarity indexes to their locations.
        """
        return {}

    def list_few_shots(self) -> List[FewShotExample]:
        """
        List all examples to be injected into few-shot prompt.

        Returns:
            List of few-shot examples
        """
        return []
