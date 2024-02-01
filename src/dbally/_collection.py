from typing import List, Optional, Tuple, Type

from dbally.iql import IQLActions, IQLQuery
from dbally.view_selection.random_view_selector import RandomViewSelector
from dbally.views.base import AbstractBaseView, ExposedFunction
from dbally.views.registry import ViewRegistry


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


class DBAllyCollection:
    """
    Collection is a container for a set of views that can be used by db-ally to answer user questions.
    It also stores configuration such as LLM model choice, vector db or available data sources.
    """

    def __init__(self, name: str):
        self.name = name
        self._registry = ViewRegistry()
        self._view_selector = RandomViewSelector()
        self._iql_generator = IQLGeneratorMock()

    def register_view(self, view: Type[AbstractBaseView], name: Optional[str] = None) -> None:
        """
        Register new view that will be available to query via the collection.

        Args:
            view: a view type to be registered in a collection
            name: optional name of the view
        """
        self._registry.register(view, name=name)

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

        # select view
        views = self._registry.list()

        if len(views) == 0:
            raise ValueError("Empty collection")
        if len(views) == 1:
            selected_view = next(iter(views))
        else:
            selected_view = await self._view_selector.select_view(question, views)

        view = self._registry.get(selected_view)

        filter_list, action_list = view.list_filters(), view.list_actions()

        iql_filters, iql_actions = await self._iql_generator.generate_iql(question, filter_list, action_list)

        filters = IQLQuery.parse(iql_filters)
        actions = IQLActions.parse(iql_actions)

        view.apply_filters(filters)
        view.apply_actions(actions)
        sql = view.generate_sql()

        return sql
