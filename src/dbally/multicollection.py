from typing import Dict, List, Optional

import dbally
from dbally.llms.clients.base import LLMOptions

from .audit import EventHandler
from .collection import Collection
from .collection.exceptions import NoCollectionFound
from .views.base import BaseView


class MultiCollection:
    """
    Multicollection is a container for a set of collections. Collections are accessed hierarchically.
    They were designed as a fallback mechanism.

    Tip:
        It is recommended to create new Multicollection using the [`dbally.create_mulicolletion`]
        function instead of instantiating this class directly.
    """

    def __init__(
        self,
        name: str,
        collections_list: List[Collection],
    ) -> None:
        self._collection_order = [collection.name for collection in collections_list]
        self._collections = {collection.name: collection for collection in collections_list}
        self.name = name

    def add(self, collection: Collection, priority: Optional[int]) -> None:
        """
        Add new collection to list

        Args:
            collection: Collection to add
            priority: Hierarchy of collection

        """
        index = len(self._collection_order) if not priority else priority
        self._collection_order.insert(index, collection.name)
        self._collections[collection.name] = collection

    def add_event_handler(self, event_handler: EventHandler) -> None:
        """
        Adds an event handler to the list of event handlers.

        Args:
            event_handler: The event handler to be added.
        """
        for collection in self._collections.values():
            collection.add_event_handler(event_handler)

    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        Returns:
            Dictionary of view names and descriptions
        """
        result_dict = {}
        for collection in self._collections.values():
            result_dict.update(collection.list())
        return result_dict

    def get_collection(self, collection_name: str) -> Collection:
        """
        Returns an instance of the collection with the given name

        Args:
            collection_name: Name of the collection to return

        Returns:
            Collection

        Raises:
             NoCollectionFound: If there is no view with the given name
        """

        collection = self._collections.get(collection_name)

        if not collection:
            raise NoCollectionFound

        return collection

    def get(self, view_name: str) -> BaseView:
        """
        Returns an instance of the view with the given name

        Args:
            view_name: Name of the collection to return

        Returns:
            View instance

        Raises:
             NoCollectionFound: If there is no collection with the given name
        """

        for collection in self._collections.values():
            selected_collection = collection.get(view_name)
            if selected_collection:
                return selected_collection

        raise NoCollectionFound

    async def ask(
        self,
        question: str,
        dry_run: bool = False,
        return_natural_response: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> dbally.ExecutionResult:
        """
        Ask question in a text form and retrieve the answer based on the available views with hierarchical order.
        The order is set by collection place on the collection list.

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

        result = None
        for collection_name in self._collection_order:
            try:
                collection = self.get_collection(collection_name)
                result = await collection.ask(
                    question=question,
                    dry_run=dry_run,
                    return_natural_response=return_natural_response,
                    llm_options=llm_options,
                )
            except dbally.DbAllyError:
                print("Found exception")
        if not result:
            raise dbally.DbAllyError

        return result
