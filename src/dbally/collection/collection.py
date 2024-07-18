import asyncio
import inspect
import logging
import textwrap
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Type, TypeVar

import dbally
from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.event_tracker import EventTracker
from dbally.audit.events import FallbackEvent, RequestEnd, RequestStart
from dbally.collection.exceptions import IndexUpdateError, NoViewFoundError
from dbally.collection.results import ExecutionResult, ViewExecutionResult
from dbally.iql_generator.prompt import UnsupportedQueryError
from dbally.llms.base import LLM
from dbally.llms.clients.base import LLMOptions
from dbally.nl_responder.nl_responder import NLResponder
from dbally.similarity.index import AbstractSimilarityIndex
from dbally.view_selection.base import ViewSelector
from dbally.views.base import BaseView, IndexLocation

HANDLED_EXCEPTION_TYPES = (NoViewFoundError, UnsupportedQueryError, IndexUpdateError)


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
        nl_responder: NLResponder,
        event_handlers: Optional[List[EventHandler]] = None,
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
            nl_responder: Object that translates RAW response from db-ally into natural language.
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
        self._llm = llm
        self._fallback_collection: Optional[Collection] = fallback_collection
        self._event_handlers = event_handlers or dbally.event_handlers

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

    def set_fallback(self, fallback_collection: "Collection") -> "Collection":
        """
        Set fallback collection which will be asked if the ask to base collection does not succeed.

        Args:
            fallback_collection: Collection to be asked in case of base collection failure.

        Returns:
            The fallback collection to create chains call
        """
        self._fallback_collection = fallback_collection
        if fallback_collection._event_handlers != self._event_handlers:  # pylint: disable=W0212
            logging.warning(
                "Event handlers of the fallback collection are different from the base collection. "
                "Continuity of the audit trail is not guaranteed.",
            )

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

    async def _select_view(
        self,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions],
    ) -> str:
        """
        Select a view based on the provided question and options.

        If there is only one view available, it selects that view directly. Otherwise, it
        uses the view selector to choose the most appropriate view.

        Args:
            question: The question to be answered.
            event_tracker: The event tracker for logging and tracking events.
            llm_options: Options for the LLM client.

        Returns:
            str: The name of the selected view.

        Raises:
            ValueError: If the collection of views is empty.
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
        return selected_view_name

    async def _ask_view(
        self,
        selected_view_name: str,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions],
        dry_run: bool,
    ):
        """
        Ask the selected view to provide an answer to the question.

        Args:
            selected_view_name: The name of the selected view.
            question: The question to be answered.
            event_tracker: The event tracker for logging and tracking events.
            llm_options: Options for the LLM client.
            dry_run: If True, only generate the query without executing it.

        Returns:
            Any: The result from the selected view.
        """
        selected_view = self.get(selected_view_name)
        view_result = await selected_view.ask(
            query=question,
            llm=self._llm,
            event_tracker=event_tracker,
            n_retries=self.n_retries,
            dry_run=dry_run,
            llm_options=llm_options,
        )
        return view_result

    async def _generate_textual_response(
        self,
        view_result: ViewExecutionResult,
        question: str,
        event_tracker: EventTracker,
        llm_options: Optional[LLMOptions],
    ) -> str:
        """
        Generate a textual response from the view result.

        Args:
            view_result: The result from the view.
            question: The question to be answered.
            event_tracker: The event tracker for logging and tracking events.
            llm_options: Options for the LLM client.

        Returns:
            The generated textual response.
        """
        textual_response = await self._nl_responder.generate_response(
            result=view_result,
            question=question,
            event_tracker=event_tracker,
            llm_options=llm_options,
        )
        return textual_response

    def get_all_event_handlers(self) -> List[EventHandler]:
        """
        Retrieves all event handlers, including those from a fallback collection if available.

        This method returns a list of event handlers. If there is no fallback collection,
        it simply returns the event handlers stored in the current object. If a fallback
        collection is available, it combines the event handlers from both the current object
        and the fallback collection, ensuring no duplicates.

        Returns:
            A list of event handlers.
        """
        if not self._fallback_collection:
            return self._event_handlers
        return list(set(self._event_handlers).union(self._fallback_collection.get_all_event_handlers()))

    async def _handle_fallback(
        self,
        question: str,
        dry_run: bool,
        return_natural_response: bool,
        llm_options: Optional[LLMOptions],
        selected_view_name: str,
        event_tracker: EventTracker,
        caught_exception: Exception,
    ) -> ExecutionResult:
        """
        Handle fallback if the main query fails.

        Args:
            question: The question to be answered.
            dry_run: If True, only generate the query without executing it.
            return_natural_response: If True, return the natural language response.
            llm_options: Options for the LLM client.
            selected_view_name: The name of the selected view.
            event_tracker: The event tracker for logging and tracking events.
            caught_exception: The exception that was caught.

        Returns:
            The result from the fallback collection.

        """
        if not self._fallback_collection:
            raise caught_exception

        fallback_event = FallbackEvent(
            triggering_collection_name=self.name,
            triggering_view_name=selected_view_name,
            fallback_collection_name=self._fallback_collection.name,
            error_description=repr(caught_exception),
        )

        async with event_tracker.track_event(fallback_event) as span:
            result = await self._fallback_collection.ask(
                question=question,
                dry_run=dry_run,
                return_natural_response=return_natural_response,
                llm_options=llm_options,
                event_tracker=event_tracker,
            )
            span(fallback_event)
        return result

    async def ask(
        self,
        question: str,
        dry_run: bool = False,
        return_natural_response: bool = False,
        llm_options: Optional[LLMOptions] = None,
        event_tracker: Optional[EventTracker] = None,
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
            llm_options: options to use for the LLM client. If provided, these options will be merged with the default
                options provided to the LLM client, prioritizing option values other than NOT_GIVEN
            event_tracker: Event tracker object for given ask.

        Returns:
            ExecutionResult object representing the result of the query execution.

        Raises:
            ValueError: if collection is empty
            IQLError: if incorrect IQL was generated `n_retries` amount of times.
            ValueError: if incorrect IQL was generated `n_retries` amount of times.
            NoViewFoundError: if question does not match to any registered view,
            UnsupportedQueryError: if the question could not be answered
            IndexUpdateError: if index update failed
        """
        if not event_tracker:
            is_fallback_call = False
            event_handlers = self.get_all_event_handlers()
            event_tracker = EventTracker.initialize_with_handlers(event_handlers)
            await event_tracker.request_start(RequestStart(question=question, collection_name=self.name))
        else:
            is_fallback_call = True

        selected_view_name = ""

        try:
            start_time = time.monotonic()
            selected_view_name = await self._select_view(
                question=question, event_tracker=event_tracker, llm_options=llm_options
            )

            start_time_view = time.monotonic()
            view_result = await self._ask_view(
                selected_view_name=selected_view_name,
                question=question,
                event_tracker=event_tracker,
                llm_options=llm_options,
                dry_run=dry_run,
            )
            end_time_view = time.monotonic()

            natural_response = (
                await self._generate_textual_response(view_result, question, event_tracker, llm_options)
                if not dry_run and return_natural_response
                else ""
            )

            result = ExecutionResult(
                results=view_result.results,
                context=view_result.context,
                execution_time=time.monotonic() - start_time,
                execution_time_view=end_time_view - start_time_view,
                view_name=selected_view_name,
                textual_response=natural_response,
            )

        except HANDLED_EXCEPTION_TYPES as caught_exception:
            if self._fallback_collection:
                result = await self._handle_fallback(
                    question=question,
                    dry_run=dry_run,
                    return_natural_response=return_natural_response,
                    llm_options=llm_options,
                    selected_view_name=selected_view_name,
                    event_tracker=event_tracker,
                    caught_exception=caught_exception,
                )
            else:
                raise caught_exception

        if not is_fallback_call:
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
