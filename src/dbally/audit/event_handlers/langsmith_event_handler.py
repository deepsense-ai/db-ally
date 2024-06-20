import socket
from getpass import getuser
from typing import Optional

from langsmith.client import Client
from langsmith.run_trees import RunTree

from dbally.audit.event_handlers.base import EventHandler
from dbally.audit.events import Event, LLMEvent, RequestEnd, RequestStart, SimilarityEvent


class LangSmithEventHandler(EventHandler[RunTree, RunTree]):
    """
    This handler Logs events to a LangSmith instance.

    !!! tip
        To learn how to use `LangSmithEventHandler` visit
        [How-To: Log db-ally runs to LangSmith](../../how-to/log_runs_to_langsmith.md)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Constructs a new langsmith event handler instance.

        Args:
            api_key: The api key for LangSmith. If None LANGCHAIN_API_KEY environment variable will be used.
        """
        self._client = Client(api_key=api_key)

    async def request_start(self, user_request: RequestStart) -> RunTree:
        """
        Initializes the `RunTree` object with all required attributes.

        Args:
            user_request: The start of the request.

        Returns:
            run_tree object for a request span
        """
        run_tree = RunTree(
            name=f"{user_request.collection_name} by {getuser()}@{socket.gethostname()}",
            run_type="chain",
            inputs={"text": user_request.question},
            serialized={},
            client=self._client,
        )

        return run_tree

    async def event_start(self, event: Event, request_context: RunTree) -> RunTree:
        """
        Log the start of the event.

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method

        Returns:
            run_tree object for an event span

        Raises:
            ValueError: when event is invalid
        """
        if isinstance(event, LLMEvent):
            child_run = request_context.create_child(
                name=event.type,
                run_type="llm",
                inputs={"prompts": [event.prompt]},
            )
            return child_run

        if isinstance(event, SimilarityEvent):
            child_run = request_context.create_child(
                name="Similarity Lookup",
                run_type="tool",
                inputs={"input": event.input_value, "store": event.store, "fetcher": event.fetcher},
            )
            return child_run

        raise ValueError("Unsupported event")

    async def event_end(self, event: Optional[Event], request_context: RunTree, event_context: RunTree) -> None:
        """
        Log the end of the event.

        Args:
            event: Event to be logged.
            request_context: Optional context passed from request_start method
            event_context: Optional context passed from event_start method
        """
        if isinstance(event, LLMEvent):
            event_context.end(outputs={"output": event.response})
        elif isinstance(event, SimilarityEvent):
            event_context.end(outputs={"output": event.output_value})

    async def request_end(self, output: RequestEnd, request_context: RunTree) -> None:
        """
        Log the end of the request.

        Args:
            output: The output of the request. In this case - PSQL query.
            request_context: Optional context passed from request_start method
        """
        request_context.end(outputs={"sql": output.result.context["sql"]})
        request_context.post(exclude_child_runs=False)
