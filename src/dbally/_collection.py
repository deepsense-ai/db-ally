import inspect
import textwrap
from typing import Callable, Dict, List, Optional, Type, TypeVar

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_tracker import EventTracker
from dbally.data_models.audit import RequestEnd, RequestStart
from dbally.data_models.execution_result import ExecutionResult
from dbally.iql import IQLQuery
from dbally.iql._exceptions import IQLError
from dbally.iql_generator.iql_generator import IQLGenerator
from dbally.nl_responder.nl_responder import NLResponder
from dbally.utils.errors import NoViewFoundError
from dbally.view_selection.base import ViewSelector
from dbally.views.base import AbstractBaseView


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
        event_handlers: List[EventHandler],
        nl_responder: NLResponder,
        n_retries: int = 3,
    ) -> None:
        self.name = name
        self.n_retries = n_retries
        self._views: Dict[str, Callable[[], AbstractBaseView]] = {}
        self._builders: Dict[str, Callable[[], AbstractBaseView]] = {}
        self._view_selector = view_selector
        self._iql_generator = iql_generator
        self._nl_responder = nl_responder
        self._event_handlers = event_handlers

    T = TypeVar("T", bound=AbstractBaseView)

    def add(self, view: Type[T], builder: Optional[Callable[[], T]] = None, name: Optional[str] = None) -> None:
        """
        Register new view that will be available to query via the collection.

        Args:
            view: a view type to be added to the collection
            builder: optional factory function that will be used to create the view instance
            name: optional name of the view (defaults to the name of the class)

        Raises:
            ValueError: if view with the given name is already registered
        """
        if name is None:
            name = view.__name__

        if name in self._views or name in self._builders:
            raise ValueError(f"View with name {name} is already registered")

        non_default_args = any(
            p.default == inspect.Parameter.empty for p in inspect.signature(view).parameters.values()
        )
        if non_default_args and builder is None:
            raise ValueError("Builder function is required for views with non-default arguments")

        self._views[name] = view
        self._builders[name] = builder or view

    def get(self, name: str) -> AbstractBaseView:
        """
        Returns an instance of the view with the given name

        Args:
            name: Name of the view to return

        Returns:
            View instance

        Raises:
             NoViewFoundError: If there is no view with the given name
        """

        if name not in self._views:
            raise NoViewFoundError

        return self._builders[name]()

    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        :return: Dictionary of view names and descriptions
        """
        return {
            name: (textwrap.dedent(view.__doc__).strip() if view.__doc__ else "") for name, view in self._views.items()
        }

    async def ask(self, question: str, dry_run: bool = False, return_natural_response: bool = False) -> ExecutionResult:
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
            dry_run: if True, only generate the query without executing it
            return_natural_response: if True (and dry_run is False as natural response requires query results),
                                     the natural response will be included in the answer

        Returns:
            ExecutionResult object representing the result of the query execution.

        Raises:
            ValueError: if collection is empty
        """
        event_tracker = EventTracker.initialize_with_handlers(self._event_handlers)

        await event_tracker.request_start(RequestStart(question=question, collection_name=self.name))

        # select view
        views = self.list()

        if len(views) == 0:
            raise ValueError("Empty collection")
        if len(views) == 1:
            selected_view = next(iter(views))
        else:
            selected_view = await self._view_selector.select_view(question, views, event_tracker)

        view = self.get(selected_view)

        filter_list = view.list_filters()

        iql_filters, conversation = await self._iql_generator.generate_iql(
            question=question, filters=filter_list, event_tracker=event_tracker
        )

        for _ in range(self.n_retries):
            try:
                filters = await IQLQuery.parse(iql_filters, filter_list)
                await view.apply_filters(filters)
                break
            except (IQLError, ValueError) as e:
                conversation = self._iql_generator.add_error_msg(conversation, [e])
                iql_filters, conversation = await self._iql_generator.generate_iql(
                    question=question,
                    filters=filter_list,
                    event_tracker=event_tracker,
                    conversation=conversation,
                )
                continue

        result = view.execute(dry_run=dry_run)

        if not dry_run and return_natural_response:
            result.textual_response = await self._nl_responder.generate_response(
                result, question, iql_filters, event_tracker
            )

        await event_tracker.request_end(RequestEnd(result=result))

        return result
