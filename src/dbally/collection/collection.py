import abc
from typing import Dict, Optional

from dbally.audit.event_handlers.base import EventHandler
from dbally.collection.results import ExecutionResult
from dbally.llms.clients.base import LLMOptions
from dbally.views.base import BaseView


class Collection:
    """
    Collection is a container or list of containers for a set of views that can be used by db-ally to answer user
    questions.

    """

    @abc.abstractmethod
    def add(self, *args, **kwargs) -> None:
        """
        Register new container or list of containers.

        Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
        """

    @abc.abstractmethod
    def add_event_handler(self, event_handler: EventHandler):
        """
        Adds an event handler to the list of event handlers.

        Args:
            event_handler: The event handler to be added.
        """

    @abc.abstractmethod
    def get(self, name: str) -> BaseView:
        """
        Returns an instance of the view with the given name

        Args:
            name: Name of the view to return

        Returns:
            View instance

        Raises:
             NoViewFoundError: If there is no view with the given name
        """

    @abc.abstractmethod
    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        Returns:
            Dictionary of view names and descriptions
        """

    @abc.abstractmethod
    async def ask(
        self,
        question: str,
        dry_run: bool = False,
        return_natural_response: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ExecutionResult:
        """
        Ask question in a text form and retrieve the answer based on the available views.

            Question answering is composed of following steps:
                1. View Selection
                2. IQL Generation
                3. IQL Parsing
                4. Query Building
                5. Query Execution

            Args:
                question: question posed using natural language representation e.g\
                "What job offers for Data Scientists do we have?"
                dry_run: if True, only generate the query without executing it
                return_natural_response: if True (and dry_run is False as natural response requires query results),
                    the natural response will be included in the answer
                llm_options: options to use for the LLM client. If provided, these options will be merged with the
                    default options provided to the LLM client, prioritizing option values other than NOT_GIVEN

            Returns:
                ExecutionResult object representing the result of the query execution.

            Raises:
                ValueError: if collection is empty
                IQLError: if incorrect IQL was generated `n_retries` amount of times.
                ValueError: if incorrect IQL was generated `n_retries` amount of times.
        """
