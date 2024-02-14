import textwrap
from typing import Dict, List, Optional, Tuple, Type

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_store import EventStore
from dbally.data_models.audit import RequestEnd, RequestStart
from dbally.iql import IQLActions, IQLQuery
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.view_selection.base import ViewSelector
from dbally.views.base import AbstractBaseView, ExposedFunction


class IQLGeneratorMock:
    """Waiting for other PRs to be merged"""

    async def generate_iql(
        self, question: str, filters: List[ExposedFunction], actions: List[ExposedFunction]
    ) -> Tuple[str, str]:
        """
        Temp

        Args:
            question: user question
            filters: available filters
            actions: available actions

        Returns:
            IQL string
        """
        print(f"{question=} / {filters=} / {actions=}")
        return "filter_by_eye_color('Blue') and taller_than(180.0)", "sort_by_gender()"


class Collection:
    """
    Collection is a container for a set of views that can be used by db-ally to answer user questions.
    It also stores configuration such as LLM model choice, vector db or available data sources.
    """

    def __init__(
        self,
        name: str,
        view_selector: ViewSelector,
        iql_generator: IQLGenerator,
        event_handlers: List[Type[EventHandler]],
    ) -> None:
        self.name = name
        self._views: Dict[str, Type[AbstractBaseView]] = {}
        self._view_selector = view_selector
        self._iql_generator = iql_generator
        self._event_handlers = event_handlers

    def add(self, view: Type[AbstractBaseView], name: Optional[str] = None) -> None:
        """
        Register new view that will be available to query via the collection.

        Args:
            view: a view type to be added to the collection
            name: optional name of the view (defaults to the name of the class)

        Raises:
            ValueError: if view with the given name is already registered
        """
        if name is None:
            name = view.__name__

        if name in self._views:
            raise ValueError(f"View with name {name} is already registered")

        self._views[name] = view

    def get(self, name: str) -> AbstractBaseView:
        """
        Returns an instance of the view with the given name

        :param name: Name of the view to return
        :return: View instance
        """
        return self._views[name]()

    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        :return: Dictionary of view names and descriptions
        """
        return {
            name: (textwrap.dedent(view.__doc__).strip() if view.__doc__ else "") for name, view in self._views.items()
        }

    async def ask(self, question: str) -> str:
        """
        Ask question in a text form and retrieve the answer based on the available views.

        Question answering is composed of following steps:
            - View Selection
            - IQL Generation
            - IQL Parsing
            - Query Building
            - Query Execution

        Args:
             question: question in text form

        Returns:
            SQL query - TODO: it should execute query and return results

        Raises:
            ValueError: if collection is empty
        """
        event_store = EventStore.initialize_with_handlers(self._event_handlers)

        event_store.request_start(RequestStart(question=question))

        # select view
        views = self.list()

        if len(views) == 0:
            raise ValueError("Empty collection")
        if len(views) == 1:
            selected_view = next(iter(views))
        else:
            selected_view = await self._view_selector.select_view(question, views, event_store)

        view = self.get(selected_view)

        filter_list, action_list = view.list_filters(), view.list_actions()

        iql_filters, iql_actions = await self._iql_generator.generate_iql(
            question=question, filters=filter_list, actions=action_list, event_store=event_store
        )

        filters = IQLQuery.parse(iql_filters)
        actions = IQLActions.parse(iql_actions)

        view.apply_filters(filters)
        view.apply_actions(actions)
        sql = view.generate_sql()

        event_store.request_end(RequestEnd(sql=sql))

        return sql
