import asyncio
import inspect
import textwrap
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Type, TypeVar

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_tracker import EventTracker
from dbally.audit.events import RequestEnd, RequestStart
from dbally.collection.decorators import handle_exception
from dbally.collection.exceptions import IndexUpdateError, NoViewFoundError
from dbally.collection.results import ExecutionResult
from dbally.iql_generator.iql_prompt_template import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.nl_responder.nl_responder import NLResponder
from dbally.similarity.index import AbstractSimilarityIndex
from dbally.view_selection.base import ViewSelector
from dbally.views.base import BaseView, IndexLocation


class Collection:
    """
    Collection is a container for a set of views that can be used by db-ally to answer user questions.

    Tip:
        It is recommended to create new collections using the [`dbally.create_collection`][dbally.create_collection]\
        function instead of instantiating this class directly.
    """

    def __init__(
        self,
        name: str,
        view_selector: ViewSelector,
        llm: LLM,
        event_handlers: List[EventHandler],
        nl_responder: NLResponder,
        n_retries: int = 3,
        fallback_collection: Optional["Collection"] = None,
    ) -> None:
        """
        Args:
            name: Name of the collection is available for [Event handlers](event_handlers/index.md) and is\
            used to distinguish different db-ally runs.
            view_selector: As you register more than one [View](views/index.md) within single collection,\
            before generating the IQL query, a View that fits query the most is selected by the\
            [ViewSelector](view_selection/index.md).
            llm: LLM used by the collection to generate views and respond to natural language queries.
            event_handlers: Event handlers used by the collection during query executions. Can be used\
            to log events as [CLIEventHandler](event_handlers/cli_handler.md) or to validate system performance\
            as [LangSmithEventHandler](event_handlers/langsmith_handler.md).
            nl_responder: Object that translates RAW response from db-ally into natural language.
            n_retries: IQL generator may produce invalid IQL. If this is the case this argument specifies\
            how many times db-ally will try to regenerate it. Previous try with the error message is\
            appended to the chat history to guide next generations.
            fallback_collection: collection to be asked when the ask function could not find answer in views registered
            to this collection
        """
        self.name = name
        self.n_retries = n_retries
        self._views: Dict[str, Callable[[], BaseView]] = {}
        self._builders: Dict[str, Callable[[], BaseView]] = {}
        self._view_selector = view_selector
        self._nl_responder = nl_responder
        self._event_handlers = event_handlers
        self._llm = llm
        self._fallback_collection: Optional[Collection] = fallback_collection

    T = TypeVar("T", bound=BaseView)

    def add(self, view: Type[T], builder: Optional[Callable[[], T]] = None, name: Optional[str] = None) -> None:
        """
        Register new [View](views/index.md) that will be available to query via the collection.

        Args:
            view: A class inheriting from BaseView. Object of this type will be initialized during\
            query execution. We expect Class instead of object, as otherwise Views must have been implemented\
            stateless, which would be cumbersome.
            builder: Optional factory function that will be used to create the View instance. Use it when you\
            need to pass outcome of API call or database connection to the view, and it can change over time.
            name: Custom name of the view (defaults to the name of the class).

        Raises:
            ValueError: if view with the given name is already registered or views class possess some non-default\
            arguments.

        **Example** of custom `builder` usage

        ```python
            def build_dogs_df_view():
                dogs_df = request.get("https://dog.ceo/api/breeds/list")
                return DogsDFView(dogs_df)

            collection.add(DogsDFView, build_dogs_df_view)
        ```
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

        builder = builder or view

        # instantiate view to check if the builder is correct
        view_instance = builder()
        if not isinstance(view_instance, view):
            raise ValueError(f"The builder function for view {name} must return an instance of {view.__name__}")

        self._views[name] = view
        self._builders[name] = builder

    def add_event_handler(self, event_handler: EventHandler):
        """
        Adds an event handler to the list of event handlers.

        Args:
            event_handler: The event handler to be added.
        """
        self._event_handlers.append(event_handler)

    def set_fallback(self, fallback_collection: "Collection") -> "Collection":
        """
        Set fallback collection which will be asked if the ask to base collection does not succeed.

        Args:
            fallback_collection: Collection to be asked in case of base collection failure.

        Returns:
            The fallback collection to create chains call
        """
        self._fallback_collection = fallback_collection
        return fallback_collection

    def __rshift__(self, fallback_collection: "Collection"):
        """
        Add fallback collection which will be asked if the ask to base collection does not succeed.

        Args:
            fallback_collection: Collection to be asked in case of base collection failure.

        Returns:
            The fallback collection to create chains call
        """
        return self.set_fallback(fallback_collection)

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

        if name not in self._views:
            raise NoViewFoundError(name)

        return self._builders[name]()

    def list(self) -> Dict[str, str]:
        """
        Lists all registered view names and their descriptions

        Returns:
            Dictionary of view names and descriptions
        """
        return {
            name: (textwrap.dedent(view.__doc__).strip() if view.__doc__ else "") for name, view in self._views.items()
        }

    @handle_exception((UnsupportedQueryError, NoViewFoundError))
    async def _ask_question(
        self,
        question: str,
        event_tracker: EventTracker,
        dry_run: bool,
        llm_options: Optional[LLMOptions],
        return_natural_response: bool,
        start_time: float,
    ) -> ExecutionResult:
        """
        Find matching view and executes a query on the view and processes the result.

        This method performs the query on the selected view and measures the execution time. It also
        optionally generates a natural language response if `return_natural_response` is True and
        `dry_run` is False.

        Args:
            question: The query to be executed.
            event_tracker: An instance of the event tracker to record events.
            dry_run: Whether to perform a dry run without executing the actual query.
            llm_options: Options for the language model.
            return_natural_response: Whether to return a natural response.

        Returns:
            ExecutionResult: An object containing the results, context, execution time, view execution
                             time, view name, and optionally a textual response.

        Example:
            result = await self._ask_view(
                selected_view_name="example_view",
                question="What is the capital of France?",
                event_tracker=my_event_tracker,
                dry_run=False,
                llm_options={"option1": "value1"},
                return_natural_response=True)

        Raises:
            KeyError: If the specified view does not exist in the collection.
        """

        views = self.list()
        if len(views) == 0:
            raise ValueError("Empty collection")
        if len(views) == 1:
            selected_view_name = next(iter(views))
        else:
            selected_view_name = await self._view_selector.select_view(
                question=question,
                views=views,
                event_tracker=event_tracker,
                llm_options=llm_options,
            )

        selected_view = self.get(selected_view_name)
        start_time_view = time.monotonic()
        view_result = await selected_view.ask(
            query=question,
            llm=self._llm,
            event_tracker=event_tracker,
            n_retries=self.n_retries,
            dry_run=dry_run,
            llm_options=llm_options,
        )
        end_time_view = time.monotonic()

        textual_response = None
        if not dry_run and return_natural_response:
            textual_response = await self._nl_responder.generate_response(
                result=view_result,
                question=question,
                event_tracker=event_tracker,
                llm_options=llm_options,
            )

        result = ExecutionResult(
            results=view_result.results,
            context=view_result.context,
            execution_time=time.monotonic() - start_time,
            execution_time_view=end_time_view - start_time_view,
            view_name=selected_view_name,
            textual_response=textual_response,
        )
        return result

    async def ask(
        self,
        question: str,
        dry_run: bool = False,
        return_natural_response: bool = False,
        llm_options: Optional[LLMOptions] = None,
    ) -> Optional[ExecutionResult]:
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
            llm_options: options to use for the LLM client. If provided, these options will be merged with the default
                options provided to the LLM client, prioritizing option values other than NOT_GIVEN

        Returns:
            ExecutionResult object representing the result of the query execution.

        Raises:
            ValueError: if collection is empty
            IQLError: if incorrect IQL was generated `n_retries` amount of times.
            ValueError: if incorrect IQL was generated `n_retries` amount of times.
        """

        event_tracker = EventTracker.initialize_with_handlers(self._event_handlers)

        await event_tracker.request_start(RequestStart(question=question, collection_name=self.name))
        start_time = time.monotonic()

        result = await self._ask_question(
            question=question,
            start_time=start_time,
            event_tracker=event_tracker,
            dry_run=dry_run,
            llm_options=llm_options,
            return_natural_response=return_natural_response,
        )

        await event_tracker.request_end(RequestEnd(result=result))

        return result

    def get_similarity_indexes(self) -> Dict[AbstractSimilarityIndex, List[IndexLocation]]:
        """
        List all similarity indexes from all views in the collection.

        Returns:
            Mapping of similarity indexes to their locations, following view format.
            For:
                - freeform views, the format is (view_name, table_name, column_name)
                - structured views, the format is (view_name, filter_name, argument_name)
        """
        indexes = defaultdict(list)
        for view_name in self._views:
            view = self.get(view_name)
            view_indexes = view.list_similarity_indexes()
            for index, location in view_indexes.items():
                indexes[index].extend(location)
        return indexes

    async def update_similarity_indexes(self) -> None:
        """
        Update all similarity indexes from all structured views in the collection.

        Raises:
            IndexUpdateError: if updating any of the indexes fails. The exception provides `failed_indexes` attribute,
                a dictionary mapping failed indexes to their respective exceptions. Indexes not present in
                the dictionary were updated successfully.
        """
        indexes = self.get_similarity_indexes()
        update_coroutines = [index.update() for index in indexes]
        results = await asyncio.gather(*update_coroutines, return_exceptions=True)
        failed_indexes = {
            index: exception for index, exception in zip(indexes, results) if isinstance(exception, Exception)
        }
        if failed_indexes:
            failed_locations = [loc for index in failed_indexes for loc in indexes[index]]
            raise IndexUpdateError(failed_indexes, failed_locations)
