from functools import reduce

import asyncio
import inspect
import textwrap
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Type, TypeVar

from .collection import Collection, NoViewFoundError
from dbally.data_models.execution_result import ExecutionResult
from dbally.llms.clients.base import LLMOptions
from .views.base import BaseView


class MultiCollection:
    """
    Collection is a container for a set of views that can be used by db-ally to answer user questions.

    Tip:
        It is recommended to create new collections using the [`dbally.create_colletion`][dbally.create_collection]\
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

    def add(self, collection: Collection, priority=None) -> None:
        index = len(self._collection_order) if not priority else priority
        self._collection_order.insert(index, collection.name)
        self._collections[collection.name] = collection

    def list_collection_names(self):
        return [collection_name for collection_name in self._collection_order]

    def get_collection(self, collection_name: str) -> Collection:
        """
        Returns an instance of the view with the given name

        Args:
            collection_name: Name of the collection to return

        Returns:
            View instance

        Raises:
             NoViewFoundError: If there is no view with the given name
        """

        if collection_name not in self.list_collection_names():
            raise ValueError

        collection = self._collections[collection_name]
        return collection

    def get(self, view_name: str) -> BaseView:
        """
        Returns an instance of the view with the given name

        Args:
            view_name: Name of the collection to return

        Returns:
            View instance

        Raises:
             NoViewFoundError: If there is no view with the given name
        """

        print(f"looking for {view_name}")
        for collection in self._collections.values():
            collection_found = view_name in collection.list().keys()
            if collection_found:
                selected_collection = collection.get(view_name)
                print(f"found collection {view_name}")
                return selected_collection

        raise NoViewFoundError

    def get_collections_list(self):
        return self._collections.values()

    def list(self) -> List[str]:
        """
        Lists all registered view names and their descriptions

        Returns:
            Dictionary of view names and descriptions
        """
        return self._collection_order

    async def ask(
        self,
        question: str,
        dry_run: bool = False,
        return_natural_response: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> ExecutionResult:

        start_time = time.monotonic()
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
            except Exception:
                print("Found exception")

            # if result.results

        return result
